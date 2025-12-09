from typing import List, Optional, Dict, Any
from app.models.user import User, UserRole
from app.schemas.user_schemas import UserRegisterModel, UserUpdateModel, UserCreateModel
from app.extensions import db
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class UserService:
    """用户业务逻辑服务"""
    
    @staticmethod
    def get_all_users() -> List[User]:
        """获取所有用户"""
        return User.query.filter_by(status=True).all()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return User.query.filter_by(id=user_id, status=True).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return User.query.filter_by(email=email, status=True).first()
    
    @staticmethod
    def create_user(user_data: UserCreateModel) -> User:
        """创建新用户"""
        # 检查邮箱是否已存在
        existing_user = User.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("邮箱已被注册")
        
        # 检查工号/学号是否已存在
        existing_code = User.get_by_user_code(user_data.user_code)
        if existing_code:
            raise ValueError("工号/学号已被使用")
        
        # 创建新用户
        user = User(
            username=user_data.username,
            user_code=user_data.user_code,
            email=user_data.email,
            real_name=user_data.real_name,
            phone=user_data.phone,
            role=user_data.role,
            class_id=user_data.class_id
        )
        user.set_password(user_data.password)
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update_user(user_id: int, user_data: UserUpdateModel) -> Optional[User]:
        """更新用户信息"""
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        
        # 检查邮箱是否被其他用户使用
        if user_data.email and user_data.email != user.email:
            existing_user = User.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("邮箱已被其他用户使用")
        
        # 更新用户信息
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """软删除用户"""
        user = UserService.get_user_by_id(user_id)
        if not user:
            return False
        
        user.status = False
        db.session.commit()
        return True
    
    @staticmethod
    def batch_delete_users(user_ids: List[int]) -> Dict[str, Any]:
        """批量删除用户(软删除)"""
        success_count = 0
        failed_count = 0
        errors = []
        
        for user_id in user_ids:
            try:
                user = User.query.get(user_id)
                if not user:
                    failed_count += 1
                    errors.append(f"用户ID {user_id} 不存在")
                    continue
                
                user.status = False
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(f"删除用户ID {user_id} 失败: {str(e)}")
                logger.error(f"Delete user {user_id} error: {str(e)}")
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Batch delete commit error: {str(e)}")
            raise ValueError(f"批量删除提交失败: {str(e)}")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'total_count': len(user_ids),
            'errors': errors
        }
    
    @staticmethod
    def batch_import_users(file_path: str) -> Dict[str, Any]:
        """从Excel文件批量导入用户"""
        success_count = 0
        failed_count = 0
        errors = []
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 中文列名到英文列名的映射
            column_mapping = {
                '用户名': 'username',
                '工号/学号': 'user_code',
                '邮箱': 'email',
                '真实姓名': 'real_name',
                '角色': 'role',
                '手机号': 'phone',
                '班级ID': 'class_id'
            }
            
            # 重命名列(如果使用中文列名)
            df.rename(columns=column_mapping, inplace=True)
            
            # 验证必需的列
            required_columns = ['username', 'user_code', 'email', 'real_name', 'role']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                # 尝试显示中文列名提示
                missing_chinese = []
                reverse_mapping = {v: k for k, v in column_mapping.items()}
                for col in missing_columns:
                    chinese_name = reverse_mapping.get(col, col)
                    missing_chinese.append(chinese_name)
                raise ValueError(f"Excel文件缺少必需的列: {', '.join(missing_chinese)}")
            
            # 遍历每一行数据
            for index, row in df.iterrows():
                try:
                    # 验证角色
                    role_str = str(row['role']).lower()
                    if role_str not in ['admin', 'teacher', 'student']:
                        failed_count += 1
                        errors.append(f"第{index + 2}行: 无效的角色 '{row['role']}'")
                        continue
                    
                    role = UserRole(role_str)
                    
                    # 学生角色需要班级ID
                    class_id = None
                    if role == UserRole.STUDENT:
                        if 'class_id' not in df.columns or pd.isna(row.get('class_id')):
                            failed_count += 1
                            errors.append(f"第{index + 2}行: 学生角色必须提供班级ID")
                            continue
                        class_id = int(row['class_id'])
                    
                    # 检查邮箱是否已存在
                    if User.get_by_email(row['email']):
                        failed_count += 1
                        errors.append(f"第{index + 2}行: 邮箱 '{row['email']}' 已被注册")
                        continue
                    
                    # 检查工号/学号是否已存在
                    if User.get_by_user_code(row['user_code']):
                        failed_count += 1
                        errors.append(f"第{index + 2}行: 工号/学号 '{row['user_code']}' 已被使用")
                        continue
                    
                    # 创建用户
                    user = User(
                        username=row['username'],
                        user_code=row['user_code'],
                        email=row['email'],
                        real_name=row['real_name'],
                        phone=row.get('phone') if pd.notna(row.get('phone')) else None,
                        role=role,
                        class_id=class_id
                    )
                    # 设置默认密码为123456
                    user.set_password('123456')
                    
                    db.session.add(user)
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    errors.append(f"第{index + 2}行: {str(e)}")
                    logger.error(f"Import user at row {index + 2} error: {str(e)}")
            
            # 提交事务
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Batch import error: {str(e)}")
            raise ValueError(f"批量导入失败: {str(e)}")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'total_count': success_count + failed_count,
            'errors': errors
        }
    
    @staticmethod
    def search_users(keyword: str) -> List[User]:
        """搜索用户"""
        return User.query.filter(
            User.status == True,
            (User.username.contains(keyword) | User.email.contains(keyword) | User.real_name.contains(keyword))
        ).all()
