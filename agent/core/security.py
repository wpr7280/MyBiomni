from jose import jwt, JWTError
from core.config import settings
from typing import Optional

def verify_jwt_token(token: str) -> Optional[dict]:
    """验证 Spring Boot 生成的 JWT Token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def get_user_id_from_token(token: str) -> Optional[int]:
    """从 Token 中获取用户ID"""
    payload = verify_jwt_token(token)
    if payload:
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    return None
