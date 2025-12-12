def register_socketio_events():
    """注册所有WebSocket事件处理模块"""
    from . import attendance_events
    from . import interaction_events
