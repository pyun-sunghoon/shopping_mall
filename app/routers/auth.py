from fastapi import APIRouter, Response, status
from app.core.config import get_settings
from app.core.security import COOKIE_NAME, TOKEN_SECONDS, create_token
from app.schemas.auth import LoginRequest, MessageResponse, RegisterRequest, UserResponse
from app.services.auth import authenticate, register

router = APIRouter(prefix="/api/auth", tags=["인증"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterRequest):
    return register(data)


@router.post("/login", response_model=MessageResponse)
def login(data: LoginRequest, response: Response):
    user = authenticate(data)
    # HttpOnly 쿠키는 자바스크립트에서 읽을 수 없다.
    response.set_cookie(key=COOKIE_NAME, value=create_token(str(user["id"])), max_age=TOKEN_SECONDS,
                        httponly=True, secure=get_settings().cookie_secure, samesite="lax", path="/")
    return {"message": "로그인했습니다."}


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/", secure=get_settings().cookie_secure, httponly=True, samesite="lax")
    return {"message": "로그아웃했습니다."}
