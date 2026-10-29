from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt
from fastapi import HTTPException, Request, status

from app.core.config import get_settings
from app.db.client import get_supabase

COOKIE_NAME = "access_token"
TOKEN_SECONDS = 60 * 60 * 8


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": user_id, "iat": now, "exp": now + timedelta(seconds=TOKEN_SECONDS)},
        get_settings().secret_key.get_secret_value(), algorithm="HS256",
    )


def get_current_user(request: Request) -> dict:
    # 매 요청마다 탈퇴 여부를 확인한다.
    token = request.cookies.get(COOKIE_NAME)
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")
    if not token:
        raise unauthorized
    try:
        payload = jwt.decode(token, get_settings().secret_key.get_secret_value(), algorithms=["HS256"], options={"require": ["sub", "exp", "iat"]})
        user_id = str(UUID(payload["sub"]))
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise unauthorized
    result = get_supabase().table("users").select("id,email,name,phone,address,deleted_at").eq("id", user_id).is_("deleted_at", "null").limit(1).execute()
    if not result.data:
        raise unauthorized
    return result.data[0]
