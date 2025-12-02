import functools
import time
from typing import Callable, Any
from flask import request, jsonify

def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """简单的速率限制装饰器"""
    request_counts = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # 清理过期的记录
            request_counts[client_ip] = [
                req_time for req_time in request_counts.get(client_ip, [])
                if current_time - req_time < window_seconds
            ]
            
            # 检查请求次数
            if len(request_counts.get(client_ip, [])) >= max_requests:
                return jsonify({'message': 'Rate limit exceeded'}), 429
            
            # 记录当前请求
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            request_counts[client_ip].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_api_call(func: Callable) -> Callable:
    """API调用日志装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # 记录请求信息
        print(f"API Call: {request.method} {request.path}")
        print(f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
        print(f"IP: {request.remote_addr}")
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            print(f"API Call completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"API Call failed in {duration:.3f}s: {str(e)}")
            raise
    
    return wrapper

def validate_json(required_fields: list = None):
    """JSON数据验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({'message': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'message': 'Invalid JSON data'}), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'message': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cache_response(timeout: int = 300):
    """响应缓存装饰器（简单实现）"""
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{request.path}:{request.query_string.decode()}"
            current_time = time.time()
            
            # 检查缓存
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if current_time - cached_time < timeout:
                    return cached_data
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            return result
        return wrapper
    return decorator
