from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from postgrest.exceptions import APIError
from app.core.security import get_current_user
from app.db.client import get_supabase
from app.schemas.shop import CartAdd, CartQuantity, PaymentRequest
from app.services import shop

router = APIRouter(prefix="/api", tags=["상품 · 장바구니 · 주문 · 결제"])


@router.get("/products")
def list_products():
    return shop.products()


@router.get("/products/{product_id}")
def get_product(product_id: UUID):
    return shop.product(product_id)


@router.get("/cart")
def get_cart(user: dict = Depends(get_current_user)):
    return shop.cart(user["id"])


@router.post("/cart/items", status_code=201)
def add_item(data: CartAdd, user: dict = Depends(get_current_user)):
    # 장바구니 변경도 주문 생성과 같은 행 잠금을 사용한다.
    return {"item_id": shop.rpc("cart_add_item", {"p_user_id": user["id"], "p_product_id": str(data.product_id), "p_quantity": data.quantity})}


@router.patch("/cart/items/{item_id}")
def update_item(item_id: UUID, data: CartQuantity, user: dict = Depends(get_current_user)):
    shop.rpc("cart_update_item", {"p_user_id": user["id"], "p_item_id": str(item_id), "p_quantity": data.quantity})
    return {"message": "수량을 변경했습니다."}


@router.delete("/cart/items/{item_id}", status_code=204)
def delete_item(item_id: UUID, user: dict = Depends(get_current_user)):
    shop.rpc("cart_delete_item", {"p_user_id": user["id"], "p_item_id": str(item_id)})
    return Response(status_code=204)


@router.post("/orders", status_code=201)
def create_order(user: dict = Depends(get_current_user)):
    current = shop.cart(user["id"])
    if current["id"] is None:
        raise HTTPException(400, "장바구니가 비어 있습니다.")
    order_id = shop.rpc("create_order", {"p_user_id": user["id"], "p_order_id": current["id"]})
    return {"order_id": order_id, "status": "pending"}


@router.post("/orders/{order_id}/payment")
def pay(order_id: UUID, data: PaymentRequest, user: dict = Depends(get_current_user)):
    payment_id = shop.rpc("pay_order", {"p_user_id": user["id"], "p_order_id": str(order_id), "p_success": data.success})
    return {"payment_id": payment_id, "status": "success" if data.success else "failed"}

@router.post("/orders/direct", status_code=201)
def create_direct_order(data: CartAdd, user: dict = Depends(get_current_user)):
    order_id = shop.rpc("create_direct_order", {"p_user_id": user["id"], "p_product_id": str(data.product_id), "p_quantity": data.quantity})
    return {"order_id": order_id, "status": "pending"}
