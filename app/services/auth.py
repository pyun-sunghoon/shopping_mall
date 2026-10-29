from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from app.core.security import hash_password, verify_password
from app.db.client import get_supabase
from app.schemas.auth import LoginRequest, RegisterRequest


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register(data: RegisterRequest) -> dict:
    client = get_supabase()
    try:
        result = client.table("users").insert({
            "email": normalize_email(str(data.email)),
            "password_hash": hash_password(data.password),
            "name": data.name, "phone": data.phone, "address": data.address,
        }).execute()
    except APIError as exc:
        if exc.code == "23505":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용 중인 이메일입니다.") from exc
        raise
    if not result.data:
        raise HTTPException(status_code=500, detail="회원가입을 완료하지 못했습니다.")
    return result.data[0]


def authenticate(data: LoginRequest) -> dict:
    result = get_supabase().table("users").select("id,email,name,phone,address,password_hash,deleted_at").eq("email", normalize_email(str(data.email))).limit(1).execute()
    user = result.data[0] if result.data else None
    if not user or user["deleted_at"] is not None or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    return user
