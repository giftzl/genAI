from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# 定义角色枚举
class RoleEnum(str, Enum):
    END_USER = "end_user"
    DEVELOPER = "developer"
    ADMINISTRATOR = "administrator"
    DATA_STEWARD = "data_steward"
    SUPER_ADMIN = "super_admin"

# 定义权限枚举
class PermissionEnum(str, Enum):
    # 基础权限
    EXECUTE_AGENT = "execute_agent"
    VIEW_HISTORY = "view_history"
    
    # 开发权限
    CREATE_AGENT = "create_agent"
    EDIT_AGENT = "edit_agent"
    TEST_AGENT = "test_agent"
    SUBMIT_AGENT = "submit_agent"
    READ_DATA = "read_data"
    
    # 管理权限
    APPROVE_AGENT = "approve_agent"
    PUBLISH_AGENT = "publish_agent"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MONITOR_SYSTEM = "monitor_system"
    MANAGE_MODELS = "manage_models"
    
    # 数据权限
    MANAGE_DATA_ACCESS = "manage_data_access"
    AUDIT_DATA_ACCESS = "audit_data_access"
    REVOKE_ACCESS = "revoke_access"
    
    # 超级管理员权限
    FULL_ACCESS = "full_access"

# 角色权限映射
ROLE_PERMISSIONS = {
    RoleEnum.END_USER: [
        PermissionEnum.EXECUTE_AGENT,
        PermissionEnum.VIEW_HISTORY,
    ],
    RoleEnum.DEVELOPER: [
        PermissionEnum.EXECUTE_AGENT,
        PermissionEnum.VIEW_HISTORY,
        PermissionEnum.CREATE_AGENT,
        PermissionEnum.EDIT_AGENT,
        PermissionEnum.TEST_AGENT,
        PermissionEnum.SUBMIT_AGENT,
        PermissionEnum.READ_DATA,
    ],
    RoleEnum.ADMINISTRATOR: [
        PermissionEnum.EXECUTE_AGENT,
        PermissionEnum.VIEW_HISTORY,
        PermissionEnum.CREATE_AGENT,
        PermissionEnum.EDIT_AGENT,
        PermissionEnum.TEST_AGENT,
        PermissionEnum.SUBMIT_AGENT,
        PermissionEnum.READ_DATA,
        PermissionEnum.APPROVE_AGENT,
        PermissionEnum.PUBLISH_AGENT,
        PermissionEnum.MANAGE_USERS,
        PermissionEnum.MANAGE_ROLES,
        PermissionEnum.MONITOR_SYSTEM,
        PermissionEnum.MANAGE_MODELS,
    ],
    RoleEnum.DATA_STEWARD: [
        PermissionEnum.MANAGE_DATA_ACCESS,
        PermissionEnum.AUDIT_DATA_ACCESS,
        PermissionEnum.REVOKE_ACCESS,
        PermissionEnum.VIEW_HISTORY,
    ],
    RoleEnum.SUPER_ADMIN: [
        PermissionEnum.FULL_ACCESS,
    ],
}

# Pydantic 模型
class User(BaseModel):
    id: int
    username: str
    email: str
    roles: List[RoleEnum]
    is_active: bool = True
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    roles: List[RoleEnum] = [RoleEnum.END_USER]

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    permissions: List[str] = []

