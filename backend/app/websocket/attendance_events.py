"""
考勤相关的WebSocket事件处理
"""
from flask_socketio import emit, join_room, leave_room, disconnect
from flask import request
from app.extensions import socketio
from app.utils.auth_decorators import verify_token
import logging

logger = logging.getLogger(__name__)

# 存储用户连接信息
connected_users = {}  # {sid: {user_id, username, role}}


@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    try:
        from flask import session
        
        # 优先使用session认证
        user_id = session.get('user_id')
        username = session.get('username')
        role = session.get('role')
        
        # 如果session中没有用户信息，尝试使用token
        if not user_id:
            token = request.args.get('token')
            if token:
                user_info = verify_token(token)
                if user_info:
                    user_id = user_info['user_id']
                    username = user_info['username']
                    role = user_info['role']
        
        # 如果仍然没有用户信息，拒绝连接
        if not user_id:
            logger.warning(f"Connection rejected: No valid session or token")
            return False
        
        # 保存用户信息
        sid = request.sid
        connected_users[sid] = {
            'user_id': user_id,
            'username': username,
            'role': role
        }
        
        # 加入用户专属房间
        join_room(f"user_{user_id}")
        
        # 根据角色加入不同房间
        if role == 'student':
            join_room('students')
        elif role == 'teacher':
            join_room('teachers')
        
        logger.info(f"User connected: {username} (ID: {user_id}, Role: {role})")
        
        # 发送连接成功消息
        emit('connected', {
            'message': '连接成功',
            'user_id': user_id,
            'username': username,
            'role': role
        })
        
        return True
        
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    try:
        sid = request.sid
        if sid in connected_users:
            user_info = connected_users[sid]
            logger.info(f"User disconnected: {user_info['username']} (ID: {user_info['user_id']})")
            
            # 离开所有房间
            leave_room(f"user_{user_info['user_id']}")
            if user_info['role'] == 'student':
                leave_room('students')
            elif user_info['role'] == 'teacher':
                leave_room('teachers')
            
            # 删除用户信息
            del connected_users[sid]
    except Exception as e:
        logger.error(f"Disconnect error: {str(e)}")


@socketio.on('join_attendance')
def handle_join_attendance(data):
    """加入考勤房间"""
    try:
        sid = request.sid
        if sid not in connected_users:
            emit('error', {'message': '未认证'})
            return
        
        attendance_id = data.get('attendance_id')
        if not attendance_id:
            emit('error', {'message': '缺少考勤ID'})
            return
        
        # 加入考勤房间
        room = f"attendance_{attendance_id}"
        join_room(room)
        
        user_info = connected_users[sid]
        logger.info(f"User {user_info['username']} joined attendance room: {room}")
        
        emit('joined_attendance', {
            'message': '已加入考勤房间',
            'attendance_id': attendance_id
        })
        
    except Exception as e:
        logger.error(f"Join attendance error: {str(e)}")
        emit('error', {'message': str(e)})


@socketio.on('leave_attendance')
def handle_leave_attendance(data):
    """离开考勤房间"""
    try:
        sid = request.sid
        if sid not in connected_users:
            return
        
        attendance_id = data.get('attendance_id')
        if not attendance_id:
            return
        
        # 离开考勤房间
        room = f"attendance_{attendance_id}"
        leave_room(room)
        
        user_info = connected_users[sid]
        logger.info(f"User {user_info['username']} left attendance room: {room}")
        
    except Exception as e:
        logger.error(f"Leave attendance error: {str(e)}")


# ==================== 服务端主动推送的函数 ====================

def notify_attendance_created(attendance_data, class_id):
    """
    通知学生有新的考勤任务
    
    Args:
        attendance_data: 考勤数据
        class_id: 班级ID
    """
    try:
        logger.info(f"Broadcasting new attendance to class {class_id}: {attendance_data.get('title')}")
        
        # 向所有学生广播
        socketio.emit('attendance_created', {
            'message': '新的签到通知',
            'attendance': attendance_data
        }, room='students')
        
    except Exception as e:
        logger.error(f"Error broadcasting attendance created: {str(e)}")


def notify_attendance_updated(attendance_data):
    """
    通知考勤更新
    
    Args:
        attendance_data: 考勤数据
    """
    try:
        attendance_id = attendance_data.get('id')
        logger.info(f"Broadcasting attendance update: {attendance_id}")
        
        # 向考勤房间广播
        socketio.emit('attendance_updated', {
            'message': '考勤已更新',
            'attendance': attendance_data
        }, room=f"attendance_{attendance_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting attendance updated: {str(e)}")


def notify_attendance_started(attendance_data):
    """
    通知考勤开始
    
    Args:
        attendance_data: 考勤数据
    """
    try:
        attendance_id = attendance_data.get('id')
        logger.info(f"Broadcasting attendance started: {attendance_id}")
        
        # 向学生广播
        socketio.emit('attendance_started', {
            'message': '签到已开始',
            'attendance': attendance_data
        }, room='students')
        
        # 向考勤房间广播
        socketio.emit('attendance_started', {
            'message': '签到已开始',
            'attendance': attendance_data
        }, room=f"attendance_{attendance_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting attendance started: {str(e)}")


def notify_attendance_ended(attendance_data):
    """
    通知考勤结束
    
    Args:
        attendance_data: 考勤数据
    """
    try:
        attendance_id = attendance_data.get('id')
        logger.info(f"Broadcasting attendance ended: {attendance_id}")
        
        # 向考勤房间广播
        socketio.emit('attendance_ended', {
            'message': '签到已结束',
            'attendance': attendance_data
        }, room=f"attendance_{attendance_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting attendance ended: {str(e)}")


def notify_student_checked_in(attendance_id, student_data, record_data):
    """
    通知学生签到成功
    
    Args:
        attendance_id: 考勤ID
        student_data: 学生数据
        record_data: 签到记录数据
    """
    try:
        student_id = student_data.get('id')
        logger.info(f"Notifying student {student_id} checked in for attendance {attendance_id}")
        
        # 向学生个人发送
        socketio.emit('check_in_success', {
            'message': '签到成功',
            'attendance_id': attendance_id,
            'record': record_data
        }, room=f"user_{student_id}")
        
        # 向考勤房间广播（教师可以看到）
        socketio.emit('student_checked_in', {
            'message': f"{student_data.get('real_name')} 已签到",
            'attendance_id': attendance_id,
            'student': student_data,
            'record': record_data
        }, room=f"attendance_{attendance_id}")
        
    except Exception as e:
        logger.error(f"Error notifying check in: {str(e)}")


def notify_qrcode_refreshed(attendance_id, qrcode_data):
    """
    通知二维码已刷新
    
    Args:
        attendance_id: 考勤ID
        qrcode_data: 二维码数据
    """
    try:
        logger.info(f"Broadcasting QR code refresh for attendance {attendance_id}")
        
        # 向考勤房间广播
        socketio.emit('qrcode_refreshed', {
            'message': '二维码已刷新',
            'attendance_id': attendance_id,
            'qrcode': qrcode_data
        }, room=f"attendance_{attendance_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting QR code refresh: {str(e)}")


def get_connected_users_count():
    """获取当前连接用户数"""
    return len(connected_users)


def get_connected_users_info():
    """获取当前连接用户信息"""
    return list(connected_users.values())
