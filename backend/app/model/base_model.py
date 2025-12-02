"""
Pydantic基础模型
提供驼峰命名转换功能
"""
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """
    驼峰命名基类
    
    所有继承此类的模型会自动将Python下划线命名转换为驼峰式命名
    用于OpenAPI文档和JSON序列化
    
    示例:
        user_name -> userName
        created_at -> createdAt
        is_active -> isActive
    """
    model_config = ConfigDict(
        # 自动将字段名转换为驼峰命名
        alias_generator=to_camel,
        # 允许使用原字段名或别名进行赋值
        populate_by_name=True,
        # 支持从ORM对象创建(如SQLAlchemy模型)
        from_attributes=True
    )
