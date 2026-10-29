from datetime import datetime, timezone

from fastapi import HTTPException
from app.core.security import hash_password, verify_password
from app.db.client import get_supabase
from app.schemas.account import ProfileUpdate


def update_profile(user_id: str, data: ProfileUpdate) -> dict:
    values = data.model_dump()
    values["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = get_supabase().table("users").update(values).eq("id", user_id).is_("deleted_at", "null").execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return result.data[0]


def check_password(user_id: str, password: str) -> str:
    result = get_supabase().table("users").select("password_hash").eq("id", user_id).is_("deleted_at", "null").limit(1).execute()
    if not result.data or not verify_password(password, result.data[0]["password_hash"]):
        raise HTTPException(status_code=401, detail="현재 비밀번호가 올바르지 않습니다.")
    return result.data[0]["password_hash"]


def change_password(user_id: str, current_password: str, new_password: str) -> None:
    old_hash = check_password(user_id, current_password)
    # 비밀번호가 동시에 변경된 경우 기존 해시가 일치할 때만 갱신한다.
    result = get_supabase().table("users").update({"password_hash": hash_password(new_password), "updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", user_id).eq("password_hash", old_hash).is_("deleted_at", "null").execute()
    if not result.data:
        raise HTTPException(status_code=409, detail="회원정보가 변경되었습니다. 다시 시도해 주세요.")


def delete_account(user_id: str, password: str) -> None:
    old_hash = check_password(user_id, password)
    now = datetime.now(timezone.utc).isoformat()
    # 회원 행은 유지하여 주문 및 결제 내역을 보존한다.
    result = get_supabase().table("users").update({"deleted_at": now, "updated_at": now}).eq("id", user_id).eq("password_hash", old_hash).is_("deleted_at", "null").execute()
    if not result.data:
        raise HTTPException(status_code=409, detail="회원정보가 변경되었습니다. 다시 시도해 주세요.")


def purchase_history(user_id: str) -> list:
    # 반드시 현재 회원의 결제 완료 주문만 조회한다.
    result = get_supabase().table("orders").select(
        "id,status,created_at,updated_at,order_items(id,product_id,quantity,unit_price,products(name)),payments(amount,status,created_at)"
    ).eq("user_id", user_id).eq("status", "paid").order("created_at", desc=True).execute()
    return result.data
