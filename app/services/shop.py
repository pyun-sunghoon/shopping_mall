from uuid import UUID
from fastapi import HTTPException
from postgrest.exceptions import APIError
from app.db.client import get_supabase


def products():
    return get_supabase().table("products").select("id,name,description,price,stock,image_url").order("created_at").execute().data


def product(product_id: UUID):
    rows = get_supabase().table("products").select("id,name,description,price,stock,image_url").eq("id", str(product_id)).limit(1).execute().data
    if not rows:
        raise HTTPException(404, "상품을 찾을 수 없습니다.")
    return rows[0]


def cart(user_id: str, create: bool = False):
    db = get_supabase()
    rows = db.table("orders").select("id,status").eq("user_id", user_id).eq("status", "cart").limit(1).execute().data
    if not rows and create:
        try:
            rows = db.table("orders").insert({"user_id": user_id, "status": "cart"}).execute().data
        except APIError as exc:
            if exc.code != "23505":
                raise
            rows = db.table("orders").select("id,status").eq("user_id", user_id).eq("status", "cart").limit(1).execute().data
    if not rows:
        return {"id": None, "status": "cart", "items": []}
    order = rows[0]
    order["items"] = db.table("order_items").select("id,product_id,quantity,unit_price,products(id,name,price,stock,image_url)").eq("order_id", order["id"]).execute().data
    return order


def rpc(name: str, params: dict):
    try:
        return get_supabase().rpc(name, params).execute().data
    except APIError as exc:
        message = str(exc)
        for code, detail, status in (
            ("CART_NOT_FOUND", "장바구니를 찾을 수 없습니다.", 404),
            ("CART_EMPTY", "장바구니가 비어 있습니다.", 400),
            ("PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.", 404),
            ("ITEM_NOT_FOUND", "장바구니 항목을 찾을 수 없습니다.", 404),
            ("INVALID_QUANTITY", "수량이 허용 범위를 벗어났습니다.", 400),
            ("ORDER_NOT_PENDING", "결제 대기 중인 주문을 찾을 수 없습니다.", 404),
            ("INSUFFICIENT_STOCK", "재고가 부족합니다.", 409),
        ):
            if code in message:
                raise HTTPException(status, detail) from exc
        raise

