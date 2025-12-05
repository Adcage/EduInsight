"""
弹幕服务层
处理弹幕相关的业务逻辑
"""
from typing import List, Optional, Dict, Any, Set
from app.models.interaction import Barrage, Question
from app.models.user import User
from app.models.course import Course
from app.extensions import db
from app.schemas.interaction_schemas import BarrageCreateModel
import logging
import re

logger = logging.getLogger(__name__)


class BarrageService:
    """弹幕业务逻辑服务"""
    
    # ==================== 敏感词库 ====================
    # 实际项目中应该从数据库或配置文件加载
    SENSITIVE_WORDS = {
        # 示例敏感词（实际使用时需要完善）
        '敏感词1', '敏感词2', '违禁词', '不良信息',
        '政治敏感', '暴力', '色情', '赌博',
        # 可以添加更多敏感词
    }
    
    # ==================== 敏感词过滤 ====================
    
    @staticmethod
    def build_dfa_tree(sensitive_words: Set[str]) -> Dict[str, Any]:
        """
        构建DFA（确定有限状态自动机）字典树
        用于高效的敏感词匹配
        
        Args:
            sensitive_words: 敏感词集合
            
        Returns:
            DFA字典树
        """
        dfa_tree = {}
        
        for word in sensitive_words:
            current_dict = dfa_tree
            for char in word:
                # 如果字符不在当前字典中，添加它
                if char not in current_dict:
                    current_dict[char] = {}
                current_dict = current_dict[char]
            # 标记词的结束
            current_dict['is_end'] = True
        
        return dfa_tree
    
    @staticmethod
    def filter_sensitive_words(content: str, replace_char: str = '*') -> tuple[str, List[str]]:
        """
        敏感词过滤（DFA算法）
        
        Args:
            content: 原始内容
            replace_char: 替换字符
            
        Returns:
            (过滤后的内容, 检测到的敏感词列表)
        """
        if not content:
            return content, []
        
        # 构建DFA树
        dfa_tree = BarrageService.build_dfa_tree(BarrageService.SENSITIVE_WORDS)
        
        filtered_content = list(content)
        detected_words = []
        i = 0
        
        while i < len(content):
            current_dict = dfa_tree
            j = i
            matched_word = ""
            
            # 尝试匹配敏感词
            while j < len(content) and content[j] in current_dict:
                matched_word += content[j]
                current_dict = current_dict[content[j]]
                j += 1
                
                # 如果匹配到完整的敏感词
                if 'is_end' in current_dict:
                    # 记录检测到的敏感词
                    detected_words.append(matched_word)
                    
                    # 替换敏感词
                    for k in range(i, j):
                        filtered_content[k] = replace_char
                    
                    i = j
                    break
            else:
                i += 1
        
        return ''.join(filtered_content), detected_words
    
    @staticmethod
    def simple_filter_sensitive_words(content: str, replace_char: str = '*') -> tuple[str, List[str]]:
        """
        简单的敏感词过滤（字符串替换）
        适用于敏感词数量较少的情况
        
        Args:
            content: 原始内容
            replace_char: 替换字符
            
        Returns:
            (过滤后的内容, 检测到的敏感词列表)
        """
        if not content:
            return content, []
        
        filtered_content = content
        detected_words = []
        
        for word in BarrageService.SENSITIVE_WORDS:
            if word in filtered_content:
                detected_words.append(word)
                filtered_content = filtered_content.replace(word, replace_char * len(word))
        
        return filtered_content, detected_words
    
    @staticmethod
    def check_content_safety(content: str) -> tuple[bool, List[str]]:
        """
        检查内容安全性
        
        Args:
            content: 待检查的内容
            
        Returns:
            (是否安全, 检测到的敏感词列表)
        """
        _, detected_words = BarrageService.filter_sensitive_words(content)
        is_safe = len(detected_words) == 0
        
        return is_safe, detected_words
    
    # ==================== 弹幕CRUD操作 ====================
    
    @staticmethod
    def create_barrage(user_id: int, barrage_data: BarrageCreateModel) -> Barrage:
        """
        创建弹幕（自由弹幕，不关联问题）
        
        Args:
            user_id: 用户ID
            barrage_data: 弹幕数据
            
        Returns:
            创建的弹幕对象
            
        Raises:
            ValueError: 数据验证失败或包含敏感词
        """
        # 验证课程是否存在
        course = Course.query.get(barrage_data.course_id)
        if not course:
            raise ValueError("课程不存在")
        
        # 验证用户是否存在
        user = User.query.get(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 敏感词过滤
        filtered_content, detected_words = BarrageService.filter_sensitive_words(
            barrage_data.content
        )
        
        # 如果检测到敏感词，记录日志并抛出异常
        if detected_words:
            logger.warning(
                f"Sensitive words detected in barrage from user {user_id}: {detected_words}"
            )
            raise ValueError(f"内容包含敏感词: {', '.join(detected_words)}")
        
        # 创建弹幕
        barrage = Barrage(
            content=filtered_content,
            course_id=barrage_data.course_id,
            user_id=user_id,
            question_id=None,  # 自由弹幕，不关联问题
            is_anonymous=barrage_data.is_anonymous,
            status=True
        )
        
        try:
            db.session.add(barrage)
            db.session.commit()
            logger.info(f"Barrage created: {barrage.id} by user {user_id}")
            return barrage
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating barrage: {str(e)}")
            raise
    
    @staticmethod
    def create_answer_barrage(
        user_id: int,
        course_id: int,
        question_id: int,
        content: str,
        is_anonymous: bool = False
    ) -> Barrage:
        """
        创建答案弹幕（关联问题）
        此方法由 QuestionService 调用
        
        Args:
            user_id: 用户ID
            course_id: 课程ID
            question_id: 问题ID
            content: 弹幕内容
            is_anonymous: 是否匿名
            
        Returns:
            创建的弹幕对象
            
        Raises:
            ValueError: 数据验证失败
        """
        # 验证问题是否存在
        question = Question.query.get(question_id)
        if not question:
            raise ValueError("问题不存在")
        
        # 敏感词过滤（答案弹幕也需要过滤）
        filtered_content, detected_words = BarrageService.filter_sensitive_words(content)
        
        if detected_words:
            logger.warning(
                f"Sensitive words detected in answer barrage from user {user_id}: {detected_words}"
            )
            # 答案弹幕如果包含敏感词，仍然创建但使用过滤后的内容
            # 也可以选择抛出异常，根据业务需求决定
        
        # 创建答案弹幕
        barrage = Barrage(
            content=filtered_content,
            course_id=course_id,
            user_id=user_id,
            question_id=question_id,  # ⭐ 关联问题ID
            is_anonymous=is_anonymous,
            status=True
        )
        
        try:
            db.session.add(barrage)
            db.session.commit()
            logger.info(f"Answer barrage created: {barrage.id} for question {question_id}")
            return barrage
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating answer barrage: {str(e)}")
            raise
    
    @staticmethod
    def get_barrage_by_id(barrage_id: int) -> Optional[Barrage]:
        """
        根据ID获取弹幕
        
        Args:
            barrage_id: 弹幕ID
            
        Returns:
            弹幕对象，不存在返回None
        """
        return Barrage.query.get(barrage_id)
    
    @staticmethod
    def delete_barrage(barrage_id: int) -> bool:
        """
        删除弹幕（软删除）
        
        Args:
            barrage_id: 弹幕ID
            
        Returns:
            是否删除成功
        """
        barrage = Barrage.query.get(barrage_id)
        if not barrage:
            return False
        
        barrage.status = False
        
        try:
            db.session.commit()
            logger.info(f"Barrage deleted (soft): {barrage_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting barrage: {str(e)}")
            raise
    
    @staticmethod
    def hard_delete_barrage(barrage_id: int) -> bool:
        """
        删除弹幕（硬删除，从数据库中移除）
        
        Args:
            barrage_id: 弹幕ID
            
        Returns:
            是否删除成功
        """
        barrage = Barrage.query.get(barrage_id)
        if not barrage:
            return False
        
        try:
            db.session.delete(barrage)
            db.session.commit()
            logger.info(f"Barrage deleted (hard): {barrage_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error hard deleting barrage: {str(e)}")
            raise
    
    # ==================== 查询操作 ====================
    
    @staticmethod
    def get_barrages_by_course(
        course_id: int,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Barrage]:
        """
        获取课程的弹幕列表（最近的N条）
        
        Args:
            course_id: 课程ID
            limit: 返回数量限制
            include_deleted: 是否包含已删除的弹幕
            
        Returns:
            弹幕列表
        """
        query = Barrage.query.filter_by(course_id=course_id)
        
        if not include_deleted:
            query = query.filter_by(status=True)
        
        return query.order_by(Barrage.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_barrages_by_question(question_id: int) -> List[Barrage]:
        """
        获取问题的答案弹幕
        
        Args:
            question_id: 问题ID
            
        Returns:
            答案弹幕列表
        """
        return Barrage.query.filter_by(
            question_id=question_id,
            status=True
        ).order_by(Barrage.created_at.desc()).all()
    
    @staticmethod
    def get_free_barrages(course_id: int, limit: int = 100) -> List[Barrage]:
        """
        获取自由弹幕（不关联问题）
        
        Args:
            course_id: 课程ID
            limit: 返回数量限制
            
        Returns:
            自由弹幕列表
        """
        return Barrage.query.filter_by(
            course_id=course_id,
            question_id=None,
            status=True
        ).order_by(Barrage.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_barrages_by_user(user_id: int, limit: int = 50) -> List[Barrage]:
        """
        获取用户的弹幕列表
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            弹幕列表
        """
        return Barrage.query.filter_by(
            user_id=user_id,
            status=True
        ).order_by(Barrage.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_barrages(course_id: int, minutes: int = 10) -> List[Barrage]:
        """
        获取最近N分钟的弹幕
        
        Args:
            course_id: 课程ID
            minutes: 时间范围（分钟）
            
        Returns:
            弹幕列表
        """
        from datetime import datetime, timedelta
        
        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
        
        return Barrage.query.filter(
            Barrage.course_id == course_id,
            Barrage.status == True,
            Barrage.created_at >= time_threshold
        ).order_by(Barrage.created_at.desc()).all()
    
    # ==================== 统计操作 ====================
    
    @staticmethod
    def get_barrage_count_by_course(course_id: int) -> int:
        """
        获取课程的弹幕总数
        
        Args:
            course_id: 课程ID
            
        Returns:
            弹幕总数
        """
        return Barrage.query.filter_by(course_id=course_id, status=True).count()
    
    @staticmethod
    def get_barrage_count_by_question(question_id: int) -> int:
        """
        获取问题的答案弹幕数量
        
        Args:
            question_id: 问题ID
            
        Returns:
            答案弹幕数量
        """
        return Barrage.query.filter_by(question_id=question_id, status=True).count()
    
    @staticmethod
    def get_user_barrage_count(user_id: int) -> int:
        """
        获取用户的弹幕总数
        
        Args:
            user_id: 用户ID
            
        Returns:
            弹幕总数
        """
        return Barrage.query.filter_by(user_id=user_id, status=True).count()
    
    @staticmethod
    def get_barrage_statistics(course_id: int) -> Dict[str, Any]:
        """
        获取课程的弹幕统计信息
        
        Args:
            course_id: 课程ID
            
        Returns:
            统计信息字典
        """
        total_barrages = BarrageService.get_barrage_count_by_course(course_id)
        
        # 答案弹幕数量
        answer_barrages = Barrage.query.filter(
            Barrage.course_id == course_id,
            Barrage.question_id.isnot(None),
            Barrage.status == True
        ).count()
        
        # 自由弹幕数量
        free_barrages = Barrage.query.filter_by(
            course_id=course_id,
            question_id=None,
            status=True
        ).count()
        
        # 最近10分钟的弹幕数量
        recent_barrages = len(BarrageService.get_recent_barrages(course_id, minutes=10))
        
        return {
            'total_barrages': total_barrages,
            'answer_barrages': answer_barrages,
            'free_barrages': free_barrages,
            'recent_barrages': recent_barrages
        }
    
    # ==================== 敏感词管理 ====================
    
    @staticmethod
    def add_sensitive_word(word: str) -> bool:
        """
        添加敏感词
        
        Args:
            word: 敏感词
            
        Returns:
            是否添加成功
        """
        if word and word not in BarrageService.SENSITIVE_WORDS:
            BarrageService.SENSITIVE_WORDS.add(word)
            logger.info(f"Sensitive word added: {word}")
            return True
        return False
    
    @staticmethod
    def remove_sensitive_word(word: str) -> bool:
        """
        移除敏感词
        
        Args:
            word: 敏感词
            
        Returns:
            是否移除成功
        """
        if word in BarrageService.SENSITIVE_WORDS:
            BarrageService.SENSITIVE_WORDS.remove(word)
            logger.info(f"Sensitive word removed: {word}")
            return True
        return False
    
    @staticmethod
    def get_sensitive_words() -> List[str]:
        """
        获取所有敏感词
        
        Returns:
            敏感词列表
        """
        return list(BarrageService.SENSITIVE_WORDS)
    
    @staticmethod
    def batch_add_sensitive_words(words: List[str]) -> int:
        """
        批量添加敏感词
        
        Args:
            words: 敏感词列表
            
        Returns:
            成功添加的数量
        """
        count = 0
        for word in words:
            if BarrageService.add_sensitive_word(word):
                count += 1
        
        logger.info(f"Batch added {count} sensitive words")
        return count
