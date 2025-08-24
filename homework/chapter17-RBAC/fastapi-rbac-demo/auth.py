from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from models import User, TokenData, PermissionEnum, RoleEnum, ROLE_PERMISSIONS

# 配置
SECRET_KEY = "your-secret-key-here"  # 在生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟用户数据库
fake_users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "roles": [RoleEnum.SUPER_ADMIN],
        "is_active": True,
        "created_at": datetime.now()
    },
    "developer": {
        "id": 2,
        "username": "developer",
        "email": "dev@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "roles": [RoleEnum.DEVELOPER],
        "is_active": True,
        "created_at": datetime.now()
    },
    "user": {
        "id": 3,
        "username": "user",
        "email": "user@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "roles": [RoleEnum.END_USER],
        "is_active": True,
        "created_at": datetime.now()
    },
    "data_steward": {
        "id": 4,
        "username": "data_steward",
        "email": "data@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "roles": [RoleEnum.DATA_STEWARD],
        "is_active": True,
        "created_at": datetime.now()
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[dict]:
    """获取用户信息"""
    if username in fake_users_db:
        return fake_users_db[username]
    return None

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """验证用户身份"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def get_user_permissions(roles: List[RoleEnum]) -> List[PermissionEnum]:
    """根据角色获取用户权限"""
    permissions = set()
    for role in roles:
        if role == RoleEnum.SUPER_ADMIN:
            # 超级管理员拥有所有权限
            return list(PermissionEnum)
        role_permissions = ROLE_PERMISSIONS.get(role, [])
        permissions.update(role_permissions)
    return list(permissions)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """验证令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        permissions: List[str] = payload.get("permissions", [])
        token_data = TokenData(username=username, permissions=permissions)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token: str) -> User:
    """获取当前用户"""
    token_data = verify_token(token)
    user = get_user(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(**user)
