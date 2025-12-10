"""
课堂互动WebSocket事件处理
处理投票、提问、弹幕等实时互动事件
"""
from flask_socketio import emit, join_room, leave_room, rooms
from flask import request
from app.extensions import socketio
import logging

logger = logging.getLogger(__name__)


# ==================== 连接管理 ====================

@socketio.on('connect')
def handle_connect():
    """
    客户端连接事件
    
    当客户端建立WebSocket连接时触发
    """
    client_id = request.sid
    logger.info(f"Client connected: {client_id}")
    
    emit('connected', {
        'message': 'WebSocket连接成功',
        'client_id': client_id
    })


@socketio.on('disconnect')
def handle_disconnect():
    """
    客户端断开连接事件
    
    当客户端断开WebSocket连接时触发
    """
    client_id = request.sid
    logger.info(f"Client disconnected: {client_id}")


@socketio.on('error')
def handle_error(error):
    """
    错误处理
    """
    logger.error(f"WebSocket error: {error}")
    emit('error', {'message': str(error)})


# ==================== 房间管理 ====================

@socketio.on('join_course')
def handle_join_course(data):
    """
    加入课程房间
    
    Args:
        data: {
            'course_id': int,  # 课程ID
            'user_id': int,    # 用户ID
            'user_name': str   # 用户名（可选）
        }
    """
    try:
        course_id = data.get('course_id')
        user_id = data.get('user_id')
        user_name = data.get('user_name', f'User{user_id}')
        
        if not course_id:
            emit('error', {'message': '缺少课程ID'})
            return
        
        # 房间名称格式: course_{course_id}
        room = f'course_{course_id}'
        join_room(room)
        
        logger.info(f"User {user_id} ({user_name}) joined course room: {room}")
        
        # 通知用户加入成功
        emit('joined_course', {
            'message': f'已加入课程 {course_id}',
            'room': room,
            'course_id': course_id
        })
        
        # 通知房间内其他用户（可选）
        emit('user_joined', {
            'user_id': user_id,
            'user_name': user_name,
            'message': f'{user_name} 加入了课程'
        }, room=room, include_self=False)
        
    except Exception as e:
        logger.error(f"Error joining course: {str(e)}")
        emit('error', {'message': f'加入课程失败: {str(e)}'})


@socketio.on('leave_course')
def handle_leave_course(data):
    """
    离开课程房间
    
    Args:
        data: {
            'course_id': int,
            'user_id': int,
            'user_name': str
        }
    """
    try:
        course_id = data.get('course_id')
        user_id = data.get('user_id')
        user_name = data.get('user_name', f'User{user_id}')
        
        if not course_id:
            emit('error', {'message': '缺少课程ID'})
            return
        
        room = f'course_{course_id}'
        leave_room(room)
        
        logger.info(f"User {user_id} ({user_name}) left course room: {room}")
        
        # 通知用户离开成功
        emit('left_course', {
            'message': f'已离开课程 {course_id}',
            'room': room,
            'course_id': course_id
        })
        
        # 通知房间内其他用户（可选）
        emit('user_left', {
            'user_id': user_id,
            'user_name': user_name,
            'message': f'{user_name} 离开了课程'
        }, room=room)
        
    except Exception as e:
        logger.error(f"Error leaving course: {str(e)}")
        emit('error', {'message': f'离开课程失败: {str(e)}'})


# ==================== 投票相关事件 ====================

@socketio.on('poll_created')
def handle_poll_created(data):
    """
    投票创建通知
    
    教师创建投票后，通知房间内所有学生
    
    Args:
        data: {
            'course_id': int,
            'poll': {
                'id': int,
                'title': str,
                'description': str,
                'options': list,
                ...
            }
        }
    """
    try:
        course_id = data.get('course_id')
        poll_data = data.get('poll')
        
        if not course_id or not poll_data:
            emit('error', {'message': '缺少必要参数'})
            return
        
        room = f'course_{course_id}'
        
        # 广播给房间内所有用户
        emit('new_poll', {
            'message': '新投票已创建',
            'poll': poll_data
        }, room=room)
        
        logger.info(f"Poll {poll_data.get('id')} created notification sent to room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting poll created: {str(e)}")
        emit('error', {'message': f'广播投票失败: {str(e)}'})


@socketio.on('poll_voted')
def handle_poll_voted(data):
    """
    投票响应通知
    
    学生投票后，实时推送投票结果给教师端
    
    Args:
        data: {
            'course_id': int,
            'poll_id': int,
            'results': {
                'total_votes': int,
                'option_stats': list
            }
        }
    """
    try:
        course_id = data.get('course_id')
        poll_id = data.get('poll_id')
        results = data.get('results')
        
        if not all([course_id, poll_id, results]):
            emit('error', {'message': '缺少必要参数'})
            return
        
        room = f'course_{course_id}'
        
        # 实时推送投票结果给教师端
        emit('poll_results_updated', {
            'poll_id': poll_id,
            'results': results,
            'message': '投票结果已更新'
        }, room=room)
        
        logger.info(f"Poll {poll_id} results updated in room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting poll results: {str(e)}")
        emit('error', {'message': f'广播投票结果失败: {str(e)}'})


@socketio.on('poll_closed')
def handle_poll_closed(data):
    """
    投票关闭通知
    
    Args:
        data: {
            'course_id': int,
            'poll_id': int
        }
    """
    try:
        course_id = data.get('course_id')
        poll_id = data.get('poll_id')
        
        room = f'course_{course_id}'
        
        emit('poll_ended', {
            'poll_id': poll_id,
            'message': '投票已结束'
        }, room=room)
        
        logger.info(f"Poll {poll_id} closed notification sent to room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting poll closed: {str(e)}")


# ==================== 提问相关事件 ====================

@socketio.on('question_created')
def handle_question_created(data):
    """
    问题创建通知
    
    教师发布问题后，通知房间内所有学生
    
    Args:
        data: {
            'course_id': int,
            'question': {
                'id': int,
                'content': str,
                'is_anonymous': bool,
                ...
            }
        }
    """
    try:
        course_id = data.get('course_id')
        question_data = data.get('question')
        
        if not course_id or not question_data:
            emit('error', {'message': '缺少必要参数'})
            return
        
        room = f'course_{course_id}'
        
        emit('new_question', {
            'message': '新问题已发布',
            'question': question_data
        }, room=room)
        
        logger.info(f"Question {question_data.get('id')} created notification sent to room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting question created: {str(e)}")
        emit('error', {'message': f'广播问题失败: {str(e)}'})


@socketio.on('answer_submitted')
def handle_answer_submitted(data):
    """
    回答提交通知
    
    学生提交答案后，通知教师端
    
    Args:
        data: {
            'course_id': int,
            'question_id': int,
            'answer': {
                'id': int,
                'content': str,
                'user_id': int,
                ...
            }
        }
    """
    try:
        course_id = data.get('course_id')
        question_id = data.get('question_id')
        answer_data = data.get('answer')
        
        if not all([course_id, question_id, answer_data]):
            emit('error', {'message': '缺少必要参数'})
            return
        
        room = f'course_{course_id}'
        
        emit('new_answer', {
            'question_id': question_id,
            'answer': answer_data,
            'message': '新回答已提交'
        }, room=room)
        
        logger.info(f"Answer for question {question_id} submitted in room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting answer submitted: {str(e)}")
        emit('error', {'message': f'广播回答失败: {str(e)}'})


@socketio.on('answer_accepted')
def handle_answer_accepted(data):
    """
    答案采纳通知
    
    Args:
        data: {
            'course_id': int,
            'question_id': int,
            'answer_id': int
        }
    """
    try:
        course_id = data.get('course_id')
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        
        room = f'course_{course_id}'
        
        emit('answer_was_accepted', {
            'question_id': question_id,
            'answer_id': answer_id,
            'message': '答案已被采纳'
        }, room=room)
        
        logger.info(f"Answer {answer_id} accepted in room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting answer accepted: {str(e)}")


# ==================== 弹幕相关事件 ====================

@socketio.on('barrage_sent')
def handle_barrage_sent(data):
    """
    弹幕发送事件 ⭐ 核心功能
    
    用户发送弹幕后，实时广播给房间内所有用户
    
    Args:
        data: {
            'course_id': int,
            'barrage': {
                'id': int,
                'content': str,
                'user_id': int,
                'user_name': str,
                'question_id': int (可选，答案弹幕)
                'is_anonymous': bool,
                'created_at': str
            }
        }
    """
    try:
        course_id = data.get('course_id')
        barrage_data = data.get('barrage')
        
        if not course_id or not barrage_data:
            emit('error', {'message': '缺少必要参数'})
            return
        
        room = f'course_{course_id}'
        
        # 广播弹幕给所有在线用户（不包括发送者自己，因为发送者前端已经显示了）
        emit('new_barrage', {
            'barrage': barrage_data,
            'message': '新弹幕'
        }, room=room, include_self=False)
        
        # 判断是否为答案弹幕
        is_answer = barrage_data.get('question_id') is not None
        barrage_type = '答案弹幕' if is_answer else '自由弹幕'
        
        logger.info(f"{barrage_type} sent in room {room}: {barrage_data.get('content')[:20]}...")
        
    except Exception as e:
        logger.error(f"Error broadcasting barrage: {str(e)}")
        emit('error', {'message': f'广播弹幕失败: {str(e)}'})


@socketio.on('barrage_deleted')
def handle_barrage_deleted(data):
    """
    弹幕删除通知
    
    Args:
        data: {
            'course_id': int,
            'barrage_id': int
        }
    """
    try:
        course_id = data.get('course_id')
        barrage_id = data.get('barrage_id')
        
        room = f'course_{course_id}'
        
        emit('barrage_removed', {
            'barrage_id': barrage_id,
            'message': '弹幕已删除'
        }, room=room)
        
        logger.info(f"Barrage {barrage_id} deleted in room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting barrage deleted: {str(e)}")


# ==================== 点赞相关事件 ====================

@socketio.on('question_liked')
def handle_question_liked(data):
    """
    问题点赞通知
    
    Args:
        data: {
            'course_id': int,
            'question_id': int,
            'like_count': int
        }
    """
    try:
        course_id = data.get('course_id')
        question_id = data.get('question_id')
        like_count = data.get('like_count')
        
        room = f'course_{course_id}'
        
        emit('question_likes_updated', {
            'question_id': question_id,
            'like_count': like_count
        }, room=room)
        
    except Exception as e:
        logger.error(f"Error broadcasting question liked: {str(e)}")


@socketio.on('answer_liked')
def handle_answer_liked(data):
    """
    回答点赞通知
    
    Args:
        data: {
            'course_id': int,
            'answer_id': int,
            'like_count': int
        }
    """
    try:
        course_id = data.get('course_id')
        answer_id = data.get('answer_id')
        like_count = data.get('like_count')
        
        room = f'course_{course_id}'
        
        emit('answer_likes_updated', {
            'answer_id': answer_id,
            'like_count': like_count
        }, room=room)
        
    except Exception as e:
        logger.error(f"Error broadcasting answer liked: {str(e)}")


# ==================== 调试和监控 ====================

@socketio.on('ping')
def handle_ping():
    """
    心跳检测
    """
    emit('pong', {'message': 'pong', 'timestamp': str(request.sid)})


@socketio.on('get_room_info')
def handle_get_room_info(data):
    """
    获取房间信息（调试用）
    
    Args:
        data: {
            'course_id': int
        }
    """
    try:
        course_id = data.get('course_id')
        room = f'course_{course_id}'
        
        # 获取当前客户端所在的所有房间
        client_rooms = rooms()
        
        emit('room_info', {
            'room': room,
            'client_rooms': list(client_rooms),
            'client_id': request.sid
        })
        
    except Exception as e:
        logger.error(f"Error getting room info: {str(e)}")
        emit('error', {'message': f'获取房间信息失败: {str(e)}'})


# ==================== 点名提问相关事件 ====================

@socketio.on('call_on_student')
def handle_call_on_student(data):
    """
    教师随机点名
    
    Args:
        data: {
            'course_id': int,
            'student_id': int,
            'student_name': str
        }
    """
    try:
        course_id = data.get('course_id')
        student_id = data.get('student_id')
        student_name = data.get('student_name')
        
        if not all([course_id, student_id]):
            emit('error', {'message': '缺少必要参数'})
            return
        
        room = f'course_{course_id}'
        
        # 向课程房间广播点名通知
        emit('student_called_on', {
            'student_id': student_id,
            'student_name': student_name,
            'message': f'教师随机点名：{student_name}'
        }, room=room)
        
        logger.info(f"Student {student_id} randomly called on in course {course_id}")
        
    except Exception as e:
        logger.error(f"Error calling on student: {str(e)}")
        emit('error', {'message': f'点名失败: {str(e)}'})
