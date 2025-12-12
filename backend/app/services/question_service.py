"""
提问服务层
处理提问和回答相关的业务逻辑
"""
from typing import List, Optional, Dict, Any, Tuple
from app.models.interaction import Question, QuestionAnswer, Barrage, QuestionStatus
from app.models.user import User
from app.models.course import Course
from app.extensions import db
from app.schemas.interaction_schemas import (
    QuestionCreateModel, QuestionUpdateModel,
    QuestionAnswerCreateModel, QuestionAnswerUpdateModel
)
import logging

logger = logging.getLogger(__name__)


class QuestionService:
    """提问业务逻辑服务"""
    
    # ==================== 问题相关方法 ====================
    
    @staticmethod
    def create_question(user_id: int, question_data: QuestionCreateModel) -> Question:
        """
        创建问题
        
        Args:
            user_id: 提问者ID
            question_data: 问题数据
            
        Returns:
            创建的问题对象
            
        Raises:
            ValueError: 数据验证失败
        """
        # 验证课程是否存在
        course = Course.query.get(question_data.course_id)
        if not course:
            raise ValueError("课程不存在")
        
        # 验证用户是否存在
        user = User.query.get(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 创建问题
        question = Question(
            content=question_data.content,
            course_id=question_data.course_id,
            user_id=user_id,
            is_anonymous=question_data.is_anonymous,
            status=QuestionStatus.PENDING,
            like_count=0
        )
        
        try:
            db.session.add(question)
            db.session.commit()
            logger.info(f"Question created: {question.id} by user {user_id}")
            return question
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating question: {str(e)}")
            raise
    
    @staticmethod
    def get_question_by_id(question_id: int) -> Optional[Question]:
        """
        根据ID获取问题
        
        Args:
            question_id: 问题ID
            
        Returns:
            问题对象，不存在返回None
        """
        return Question.query.get(question_id)
    
    @staticmethod
    def get_questions_by_course(
        course_id: int,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Question], int]:
        """
        获取课程的问题列表（分页）
        
        Args:
            course_id: 课程ID
            page: 页码
            per_page: 每页数量
            status: 问题状态过滤（可选）
            
        Returns:
            (问题列表, 总数)
        """
        query = Question.query.filter_by(course_id=course_id)
        
        # 状态过滤
        if status:
            try:
                question_status = QuestionStatus(status)
                query = query.filter_by(status=question_status)
            except ValueError:
                logger.warning(f"Invalid question status: {status}")
        
        # 按创建时间倒序排列
        query = query.order_by(Question.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def get_questions_by_user(
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Question], int]:
        """
        获取用户的问题列表（分页）
        
        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            
        Returns:
            (问题列表, 总数)
        """
        query = Question.query.filter_by(user_id=user_id).order_by(Question.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def get_popular_questions(course_id: int, limit: int = 10) -> List[Question]:
        """
        获取热门问题（按点赞数排序）
        
        Args:
            course_id: 课程ID
            limit: 返回数量限制
            
        Returns:
            热门问题列表
        """
        return Question.query.filter_by(course_id=course_id).order_by(
            Question.like_count.desc()
        ).limit(limit).all()
    
    @staticmethod
    def update_question(question_id: int, question_data: QuestionUpdateModel) -> Optional[Question]:
        """
        更新问题
        
        Args:
            question_id: 问题ID
            question_data: 更新数据
            
        Returns:
            更新后的问题对象，不存在返回None
        """
        question = Question.query.get(question_id)
        if not question:
            return None
        
        # 更新字段（只更新提供的字段）
        if question_data.content is not None:
            question.content = question_data.content
        
        if question_data.status is not None:
            question.status = QuestionStatus(question_data.status.value)
        
        try:
            db.session.commit()
            logger.info(f"Question updated: {question_id}")
            return question
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating question: {str(e)}")
            raise
    
    @staticmethod
    def delete_question(question_id: int) -> bool:
        """
        删除问题
        
        Args:
            question_id: 问题ID
            
        Returns:
            是否删除成功
        """
        question = Question.query.get(question_id)
        if not question:
            return False
        
        try:
            # 级联删除会自动删除相关的回答
            db.session.delete(question)
            db.session.commit()
            logger.info(f"Question deleted: {question_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting question: {str(e)}")
            raise
    
    # ==================== 回答相关方法 ====================
    
    @staticmethod
    def create_answer(
        question_id: int, 
        user_id: int, 
        answer_data: QuestionAnswerCreateModel
    ) -> Tuple[QuestionAnswer, Barrage]:
        """
        创建回答（⭐核心功能：同时创建答案弹幕）
        
        Args:
            question_id: 问题ID
            user_id: 回答者ID
            answer_data: 回答数据
            
        Returns:
            (回答对象, 弹幕对象)
            
        Raises:
            ValueError: 数据验证失败
        """
        # 验证问题是否存在
        question = Question.query.get(question_id)
        if not question:
            raise ValueError("问题不存在")
        
        # 验证用户是否存在
        user = User.query.get(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 1. 创建回答
        answer = QuestionAnswer(
            question_id=question_id,
            user_id=user_id,
            content=answer_data.content,
            is_accepted=False,
            like_count=0
        )
        
        # 2. ⭐ 同时创建答案弹幕（核心功能）
        barrage = Barrage(
            content=answer_data.content,
            course_id=question.course_id,
            user_id=user_id,
            question_id=question_id,  # ⭐ 关键：关联问题ID，标识这是答案弹幕
            is_anonymous=False,
            status=True
        )
        
        try:
            # 3. 保存到数据库
            db.session.add(answer)
            db.session.add(barrage)
            
            # 4. 更新问题状态为已回答
            question.status = QuestionStatus.ANSWERED
            
            db.session.commit()
            
            logger.info(f"Answer created: {answer.id} for question {question_id}, barrage created: {barrage.id}")
            
            return answer, barrage
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating answer: {str(e)}")
            raise
    
    @staticmethod
    def get_answers_by_question(question_id: int) -> List[QuestionAnswer]:
        """
        获取问题的所有回答
        
        Args:
            question_id: 问题ID
            
        Returns:
            回答列表（按采纳状态、点赞数、创建时间排序）
        """
        return QuestionAnswer.query.filter_by(question_id=question_id).order_by(
            QuestionAnswer.is_accepted.desc(),  # 采纳的答案排在前面
            QuestionAnswer.like_count.desc(),   # 点赞多的排在前面
            QuestionAnswer.created_at.desc()    # 最新的排在前面
        ).all()
    
    @staticmethod
    def get_answer_by_id(answer_id: int) -> Optional[QuestionAnswer]:
        """
        根据ID获取回答
        
        Args:
            answer_id: 回答ID
            
        Returns:
            回答对象，不存在返回None
        """
        return QuestionAnswer.query.get(answer_id)
    
    @staticmethod
    def update_answer(answer_id: int, answer_data: QuestionAnswerUpdateModel) -> Optional[QuestionAnswer]:
        """
        更新回答
        
        Args:
            answer_id: 回答ID
            answer_data: 更新数据
            
        Returns:
            更新后的回答对象，不存在返回None
        """
        answer = QuestionAnswer.query.get(answer_id)
        if not answer:
            return None
        
        # 更新字段
        if answer_data.content is not None:
            answer.content = answer_data.content
        
        if answer_data.is_accepted is not None:
            # 如果要采纳此答案，需要取消同一问题下其他答案的采纳状态
            if answer_data.is_accepted:
                QuestionAnswer.query.filter_by(
                    question_id=answer.question_id,
                    is_accepted=True
                ).update({'is_accepted': False})
            
            answer.is_accepted = answer_data.is_accepted
        
        try:
            db.session.commit()
            logger.info(f"Answer updated: {answer_id}")
            return answer
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating answer: {str(e)}")
            raise
    
    @staticmethod
    def delete_answer(answer_id: int) -> bool:
        """
        删除回答
        
        Args:
            answer_id: 回答ID
            
        Returns:
            是否删除成功
        """
        answer = QuestionAnswer.query.get(answer_id)
        if not answer:
            return False
        
        try:
            db.session.delete(answer)
            db.session.commit()
            logger.info(f"Answer deleted: {answer_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting answer: {str(e)}")
            raise
    
    @staticmethod
    def accept_answer(answer_id: int) -> Optional[QuestionAnswer]:
        """
        采纳答案
        
        Args:
            answer_id: 回答ID
            
        Returns:
            采纳后的回答对象，不存在返回None
        """
        answer = QuestionAnswer.query.get(answer_id)
        if not answer:
            return None
        
        try:
            # 取消同一问题下其他答案的采纳状态
            QuestionAnswer.query.filter_by(
                question_id=answer.question_id,
                is_accepted=True
            ).update({'is_accepted': False})
            
            # 设置当前答案为采纳
            answer.is_accepted = True
            
            # 标记问题为已回答
            question = Question.query.get(answer.question_id)
            if question:
                question.status = QuestionStatus.ANSWERED
            
            db.session.commit()
            logger.info(f"Answer accepted: {answer_id}")
            return answer
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error accepting answer: {str(e)}")
            raise
    
    # ==================== 互动操作 ====================
    
    @staticmethod
    def like_question(question_id: int) -> Optional[Question]:
        """
        点赞问题
        
        Args:
            question_id: 问题ID
            
        Returns:
            点赞后的问题对象，不存在返回None
        """
        question = Question.query.get(question_id)
        if not question:
            return None
        
        question.like_count += 1
        
        try:
            db.session.commit()
            logger.info(f"Question liked: {question_id}, new count: {question.like_count}")
            return question
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error liking question: {str(e)}")
            raise
    
    @staticmethod
    def unlike_question(question_id: int) -> Optional[Question]:
        """
        取消点赞问题
        
        Args:
            question_id: 问题ID
            
        Returns:
            取消点赞后的问题对象，不存在返回None
        """
        question = Question.query.get(question_id)
        if not question:
            return None
        
        if question.like_count > 0:
            question.like_count -= 1
        
        try:
            db.session.commit()
            logger.info(f"Question unliked: {question_id}, new count: {question.like_count}")
            return question
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error unliking question: {str(e)}")
            raise
    
    @staticmethod
    def like_answer(answer_id: int) -> Optional[QuestionAnswer]:
        """
        点赞回答
        
        Args:
            answer_id: 回答ID
            
        Returns:
            点赞后的回答对象，不存在返回None
        """
        answer = QuestionAnswer.query.get(answer_id)
        if not answer:
            return None
        
        answer.like_count += 1
        
        try:
            db.session.commit()
            logger.info(f"Answer liked: {answer_id}, new count: {answer.like_count}")
            return answer
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error liking answer: {str(e)}")
            raise
    
    @staticmethod
    def unlike_answer(answer_id: int) -> Optional[QuestionAnswer]:
        """
        取消点赞回答
        
        Args:
            answer_id: 回答ID
            
        Returns:
            取消点赞后的回答对象，不存在返回None
        """
        answer = QuestionAnswer.query.get(answer_id)
        if not answer:
            return None
        
        if answer.like_count > 0:
            answer.like_count -= 1
        
        try:
            db.session.commit()
            logger.info(f"Answer unliked: {answer_id}, new count: {answer.like_count}")
            return answer
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error unliking answer: {str(e)}")
            raise
    
    # ==================== 统计和查询 ====================
    
    @staticmethod
    def get_question_with_answers(question_id: int) -> Optional[Dict[str, Any]]:
        """
        获取问题及其所有回答的详细信息
        
        Args:
            question_id: 问题ID
            
        Returns:
            包含问题和回答的字典，不存在返回None
        """
        question = Question.query.get(question_id)
        if not question:
            return None
        
        # 获取问题信息
        question_dict = question.to_dict()
        
        # 获取所有回答
        answers = QuestionService.get_answers_by_question(question_id)
        question_dict['answers'] = [answer.to_dict() for answer in answers]
        question_dict['answer_count'] = len(answers)
        
        # 获取采纳的答案
        accepted_answer = question.get_accepted_answer()
        question_dict['accepted_answer_id'] = accepted_answer.id if accepted_answer else None
        
        return question_dict
    
    @staticmethod
    def get_user_answer_count(user_id: int) -> int:
        """
        获取用户的回答总数
        
        Args:
            user_id: 用户ID
            
        Returns:
            回答总数
        """
        return QuestionAnswer.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def get_user_accepted_answer_count(user_id: int) -> int:
        """
        获取用户被采纳的回答数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            被采纳的回答数量
        """
        return QuestionAnswer.query.filter_by(user_id=user_id, is_accepted=True).count()
