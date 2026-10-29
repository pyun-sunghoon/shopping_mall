from fastapi import APIRouter, Depends, Response

from app.core.config import get_settings
from app.core.security import COOKIE_NAME, get_current_user
from app.schemas.account import AccountDelete, PasswordChange, ProfileUpdate
from app.schemas.auth import MessageResponse, UserResponse
from app.services import account

router = APIRouter(prefix="/api", tags=["회원정보 · 구매내역"])


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/", secure=get_settings().cookie_secure, httponly=True, samesite="lax")


@router.get("/me", response_model=UserResponse)
def get_profile(user: dict = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserResponse)
def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    return account.update_profile(user["id"], data)


@router.post("/me/password", response_model=MessageResponse)
def change_password(data: PasswordChange, response: Response, user: dict = Depends(get_current_user)):
    account.change_password(user["id"], data.current_password, data.new_password)
    clear_auth_cookie(response)
    return {"message": "비밀번호가 변경되었습니다. 다시 로그인해 주세요."}


@router.delete("/me", response_model=MessageResponse)
def delete_account(data: AccountDelete, response: Response, user: dict = Depends(get_current_user)):
    account.delete_account(user["id"], data.password)
    clear_auth_cookie(response)
    return {"message": "회원 탈퇴가 완료되었습니다."}


@router.get("/me/orders")
def get_purchase_history(user: dict = Depends(get_current_user)):
    return account.purchase_history(user["id"])
