"""
投票服务层
处理投票相关的业务逻辑
"""
from typing import List, Optional, Dict, Any, Tuple
from app.models.interaction import Poll, PollResponse, PollType, PollStatus
from app.models.user import User
from app.models.course import Course
from app.extensions import db
from app.schemas.interaction_schemas import PollCreateModel, PollUpdateModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PollService:
    """投票业务逻辑服务"""
    
    @staticmethod
    def create_poll(teacher_id: int, poll_data: PollCreateModel) -> Poll:
        """
        创建投票
        
        Args:
            teacher_id: 教师ID
            poll_data: 投票数据
            
        Returns:
            创建的投票对象
            
        Raises:
            ValueError: 数据验证失败
        """
        # 验证课程是否存在
        course = Course.query.get(poll_data.course_id)
        if not course:
            raise ValueError("课程不存在")
        
        # 验证教师是否存在
        teacher = User.query.get(teacher_id)
        if not teacher:
            raise ValueError("教师不存在")
        
        # 验证时间范围
        if poll_data.end_time <= poll_data.start_time:
            raise ValueError("结束时间必须晚于开始时间")
        
        # 创建投票
        poll = Poll(
            title=poll_data.title,
            description=poll_data.description,
            course_id=poll_data.course_id,
            teacher_id=teacher_id,
            poll_type=PollType(poll_data.poll_type.value),
            options=poll_data.options,
            is_anonymous=poll_data.is_anonymous,
            start_time=poll_data.start_time,
            end_time=poll_data.end_time,
            status=PollStatus.ACTIVE
        )
        
        try:
            db.session.add(poll)
            db.session.commit()
            logger.info(f"Poll created: {poll.id} by teacher {teacher_id}")
            return poll
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating poll: {str(e)}")
            raise
    
    @staticmethod
    def get_poll_by_id(poll_id: int) -> Optional[Poll]:
        """
        根据ID获取投票
        
        Args:
            poll_id: 投票ID
            
        Returns:
            投票对象，不存在返回None
        """
        return Poll.query.get(poll_id)
    
    @staticmethod
    def get_polls_by_course(
        course_id: int, 
        page: int = 1, 
        per_page: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Poll], int]:
        """
        获取课程的投票列表（分页）
        
        Args:
            course_id: 课程ID
            page: 页码
            per_page: 每页数量
            status: 投票状态过滤（可选）
            
        Returns:
            (投票列表, 总数)
        """
        query = Poll.query.filter_by(course_id=course_id)
        
        # 状态过滤
        if status:
            try:
                poll_status = PollStatus(status)
                query = query.filter_by(status=poll_status)
            except ValueError:
                logger.warning(f"Invalid poll status: {status}")
        
        # 按开始时间倒序排列
        query = query.order_by(Poll.start_time.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 自动更新过期投票的状态
        current_time = datetime.utcnow()
        for poll in pagination.items:
            if poll.status == PollStatus.ACTIVE and poll.end_time < current_time:
                poll.status = PollStatus.ENDED
                db.session.add(poll)
        
        # 提交状态更新
        if db.session.dirty:
            db.session.commit()
        
        return pagination.items, pagination.total
    
    @staticmethod
    def get_polls_by_teacher(
        teacher_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Poll], int]:
        """
        获取教师创建的投票列表（分页）
        
        Args:
            teacher_id: 教师ID
            page: 页码
            per_page: 每页数量
            
        Returns:
            (投票列表, 总数)
        """
        query = Poll.query.filter_by(teacher_id=teacher_id).order_by(Poll.start_time.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def update_poll(poll_id: int, poll_data: PollUpdateModel) -> Optional[Poll]:
        """
        更新投票
        
        Args:
            poll_id: 投票ID
            poll_data: 更新数据
            
        Returns:
            更新后的投票对象，不存在返回None
            
        Raises:
            ValueError: 数据验证失败
        """
        poll = Poll.query.get(poll_id)
        if not poll:
            return None
        
        # 更新字段（只更新提供的字段）
        if poll_data.title is not None:
            poll.title = poll_data.title
        
        if poll_data.description is not None:
            poll.description = poll_data.description
        
        if poll_data.end_time is not None:
            # 验证时间
            if poll_data.end_time <= poll.start_time:
                raise ValueError("结束时间必须晚于开始时间")
            poll.end_time = poll_data.end_time
        
        if poll_data.status is not None:
            poll.status = PollStatus(poll_data.status.value)
        
        try:
            db.session.commit()
            logger.info(f"Poll updated: {poll_id}")
            return poll
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating poll: {str(e)}")
            raise
    
    @staticmethod
    def delete_poll(poll_id: int) -> bool:
        """
        删除投票
        
        Args:
            poll_id: 投票ID
            
        Returns:
            是否删除成功
        """
        poll = Poll.query.get(poll_id)
        if not poll:
            return False
        
        try:
            # 级联删除会自动删除相关的投票响应
            db.session.delete(poll)
            db.session.commit()
            logger.info(f"Poll deleted: {poll_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting poll: {str(e)}")
            raise
    
    @staticmethod
    def close_poll(poll_id: int) -> Optional[Poll]:
        """
        关闭投票（结束投票）
        
        Args:
            poll_id: 投票ID
            
        Returns:
            更新后的投票对象，不存在返回None
        """
        poll = Poll.query.get(poll_id)
        if not poll:
            return None
        
        poll.status = PollStatus.ENDED
        
        try:
            db.session.commit()
            logger.info(f"Poll closed: {poll_id}")
            return poll
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error closing poll: {str(e)}")
            raise
    
    @staticmethod
    def vote(poll_id: int, student_id: int, selected_options: List[int]) -> PollResponse:
        """
        学生投票
        
        Args:
            poll_id: 投票ID
            student_id: 学生ID
            selected_options: 选中的选项ID列表
            
        Returns:
            投票响应对象
            
        Raises:
            ValueError: 投票验证失败
        """
        # 验证投票是否存在
        poll = Poll.query.get(poll_id)
        if not poll:
            raise ValueError("投票不存在")
        
        # 检查投票状态
        if poll.status != PollStatus.ACTIVE:
            raise ValueError("投票已结束")
        
        # 检查时间范围
        now = datetime.utcnow()
        if now < poll.start_time:
            raise ValueError("投票尚未开始")
        if now > poll.end_time:
            raise ValueError("投票已过期")
        
        # 检查是否已投票
        existing_response = PollResponse.query.filter_by(
            poll_id=poll_id,
            student_id=student_id
        ).first()
        
        if existing_response:
            raise ValueError("您已经投过票了")
        
        # 验证选项数量
        if poll.poll_type == PollType.SINGLE and len(selected_options) != 1:
            raise ValueError("单选投票只能选择一个选项")
        
        if poll.poll_type == PollType.MULTIPLE and len(selected_options) == 0:
            raise ValueError("多选投票至少选择一个选项")
        
        # 验证选项ID是否有效
        valid_option_ids = [opt['id'] for opt in poll.options]
        for option_id in selected_options:
            if option_id not in valid_option_ids:
                raise ValueError(f"无效的选项ID: {option_id}")
        
        # 创建投票响应
        response = PollResponse(
            poll_id=poll_id,
            student_id=student_id,
            selected_options=selected_options
        )
        
        try:
            db.session.add(response)
            db.session.commit()
            logger.info(f"Vote recorded: poll {poll_id}, student {student_id}")
            return response
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error recording vote: {str(e)}")
            raise
    
    @staticmethod
    def get_poll_results(poll_id: int) -> Dict[str, Any]:
        """
        获取投票结果统计
        
        Args:
            poll_id: 投票ID
            
        Returns:
            {
                'total_votes': 100,
                'option_stats': [
                    {
                        'option_id': 1,
                        'option_text': '选项A',
                        'count': 30,
                        'percentage': 30.0
                    },
                    ...
                ]
            }
            
        Raises:
            ValueError: 投票不存在
        """
        poll = Poll.query.get(poll_id)
        if not poll:
            raise ValueError("投票不存在")
        
        # 获取所有投票响应
        responses = PollResponse.query.filter_by(poll_id=poll_id).all()
        total_votes = len(responses)
        
        # 统计每个选项的票数
        option_counts = {}
        for response in responses:
            for option_id in response.selected_options:
                option_counts[option_id] = option_counts.get(option_id, 0) + 1
        
        # 计算百分比并构建结果
        option_stats = []
        for option in poll.options:
            option_id = option['id']
            count = option_counts.get(option_id, 0)
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            
            option_stats.append({
                'option_id': option_id,
                'option_text': option['text'],
                'count': count,
                'percentage': round(percentage, 2)
            })
        
        return {
            'total_votes': total_votes,
            'option_stats': option_stats
        }
    
    @staticmethod
    def check_user_voted(poll_id: int, user_id: int) -> bool:
        """
        检查用户是否已投票
        
        Args:
            poll_id: 投票ID
            user_id: 用户ID
            
        Returns:
            是否已投票
        """
        response = PollResponse.query.filter_by(
            poll_id=poll_id,
            student_id=user_id
        ).first()
        
        return response is not None
    
    @staticmethod
    def get_user_vote(poll_id: int, user_id: int) -> Optional[PollResponse]:
        """
        获取用户的投票记录
        
        Args:
            poll_id: 投票ID
            user_id: 用户ID
            
        Returns:
            投票响应对象，未投票返回None
        """
        return PollResponse.query.filter_by(
            poll_id=poll_id,
            student_id=user_id
        ).first()
    
    @staticmethod
    def get_poll_statistics(poll_id: int) -> Dict[str, Any]:
        """
        获取投票的详细统计信息
        
        Args:
            poll_id: 投票ID
            
        Returns:
            包含投票详情和统计数据的字典
        """
        poll = Poll.query.get(poll_id)
        if not poll:
            raise ValueError("投票不存在")
        
        # 基本信息
        poll_dict = poll.to_dict()
        
        # 投票结果
        results = PollService.get_poll_results(poll_id)
        
        # 合并数据
        poll_dict['results'] = results
        poll_dict['response_count'] = results['total_votes']
        
        return poll_dict
