# Flask 全局异常处理与 AOP 切面编程指南

## 概述

本指南介绍了如何在 Flask 中实现类似 Spring Boot 的全局异常处理和 AOP 切面编程功能。

## 全局异常处理

### 1. 异常类层次结构

```python
Exception
├── BusinessException (业务异常基类)
    ├── ValidationException (参数验证异常)
    ├── AuthenticationException (认证异常)
    ├── AuthorizationException (授权异常)
    └── ResourceNotFoundException (资源未找到异常)
```

### 2. 使用方式

#### 抛出业务异常
```python
from app.utils.exceptions import BusinessException, ValidationException

# 抛出业务异常
raise BusinessException("用户不存在", 404)

# 抛出验证异常
raise ValidationException("参数格式错误", {"field": "email"})
```

#### 统一响应格式
```python
from app.utils.exceptions import success_response, error_response

# 成功响应
return jsonify(success_response(data={"user_id": 123}))

# 错误响应
return jsonify(error_response("操作失败", 400))
```

### 3. 响应格式

#### 成功响应
```json
{
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {...},
    "timestamp": "2024-01-01T12:00:00"
}
```

#### 错误响应
```json
{
    "success": false,
    "code": 400,
    "message": "错误信息",
    "data": null,
    "timestamp": "2024-01-01T12:00:00",
    "path": "/api/users"
}
```

## AOP 切面编程

### 1. 可用的切面装饰器

#### @log_execution_time - 执行时间记录
```python
@log_execution_time
def my_function():
    # 自动记录方法执行时间
    pass
```

#### @require_auth - 认证切面
```python
@require_auth
def protected_endpoint():
    # 需要认证的接口
    # 认证信息存储在 g.current_user 中
    pass
```

#### @require_permission - 权限切面
```python
@require_permission('admin')
def admin_endpoint():
    # 需要特定权限的接口
    pass
```

#### @validate_json - 参数验证切面
```python
@validate_json({'name': str, 'age': int})
def create_user():
    # 自动验证 JSON 参数格式
    pass
```

#### @cache_result - 结果缓存切面
```python
@cache_result(timeout=300)  # 缓存 5 分钟
def expensive_operation():
    # 结果会被自动缓存
    pass
```

#### @rate_limit - 限流切面
```python
@rate_limit(max_requests=100, window=3600)  # 每小时最多 100 次
def api_endpoint():
    # 自动限流
    pass
```

#### @request_logging - 请求日志切面
```python
@request_logging
def api_endpoint():
    # 自动记录请求和响应日志
    pass
```

### 2. 切面组合使用

```python
@log_execution_time
@request_logging
@require_auth
@require_permission('write')
@validate_json({'title': str, 'content': str})
@rate_limit(max_requests=10, window=300)
def complex_endpoint():
    """多个切面组合使用"""
    pass
```

### 3. 全局钩子函数

```python
# 请求前执行
@app.before_request
def before_request():
    pass

# 请求后执行
@app.after_request
def after_request(response):
    return response

# 请求结束时执行
@app.teardown_request
def teardown_request(exception):
    pass
```

## 测试接口

启动应用后，可以测试以下接口：

### 1. 健康检查
```bash
GET /api/aop-demo/health
```

### 2. 认证测试
```bash
# 无认证头 - 返回 401
GET /api/aop-demo/protected

# 有效认证头 - 返回 200
GET /api/aop-demo/protected
Authorization: Bearer valid_token
```

### 3. 权限测试
```bash
GET /api/aop-demo/admin
Authorization: Bearer valid_token
```

### 4. 参数验证测试
```bash
POST /api/aop-demo/validate
Content-Type: application/json

{
    "name": "张三",
    "age": 25,
    "email": "zhangsan@example.com"
}
```

### 5. 缓存测试
```bash
# 第一次请求 - 慢
GET /api/aop-demo/cached

# 第二次请求 - 快（缓存命中）
GET /api/aop-demo/cached
```

### 6. 限流测试
```bash
# 连续请求 6 次，第 6 次会返回 429
GET /api/aop-demo/rate-limited
```

### 7. 异常测试
```bash
# 业务异常
GET /api/aop-demo/business-error?type=business

# 验证异常
GET /api/aop-demo/business-error?type=validation

# 认证异常
GET /api/aop-demo/business-error?type=auth

# 系统异常
GET /api/aop-demo/business-error?type=system
```

### 8. 复合切面测试
```bash
POST /api/aop-demo/complex
Authorization: Bearer valid_token
Content-Type: application/json

{
    "title": "测试标题",
    "content": "测试内容"
}
```

## 与 Spring Boot 的对比

| 功能 | Spring Boot | Flask |
|------|-------------|-------|
| 全局异常处理 | @ControllerAdvice + @ExceptionHandler | @app.errorhandler |
| 方法级切面 | @Aspect + @Around | 装饰器 |
| 认证切面 | Spring Security | @require_auth 装饰器 |
| 权限切面 | @PreAuthorize | @require_permission 装饰器 |
| 参数验证 | @Valid + @RequestBody | @validate_json 装饰器 |
| 缓存切面 | @Cacheable | @cache_result 装饰器 |
| 限流 | @RateLimiter | @rate_limit 装饰器 |
| 请求日志 | 拦截器 | @request_logging 装饰器 |
| 全局钩子 | 拦截器 | before_request/after_request |

## 最佳实践

1. **异常处理**
   - 定义清晰的异常层次结构
   - 使用统一的响应格式
   - 记录详细的错误日志

2. **切面编程**
   - 保持切面的单一职责
   - 注意切面的执行顺序
   - 避免过度使用切面

3. **性能考虑**
   - 缓存切面要合理设置过期时间
   - 限流切面要根据实际需求调整参数
   - 日志切面要避免记录敏感信息

4. **安全考虑**
   - 认证切面要验证 token 的有效性
   - 权限切面要实现细粒度的权限控制
   - 参数验证要防止注入攻击

## 扩展建议

1. **集成 Redis**
   - 使用 Redis 实现分布式缓存
   - 使用 Redis 实现分布式限流

2. **集成数据库**
   - 权限数据存储在数据库中
   - 用户认证信息存储在数据库中

3. **集成消息队列**
   - 异步任务处理
   - 事件驱动架构

4. **集成监控**
   - 性能监控
   - 错误监控
   - 业务监控
