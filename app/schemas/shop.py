from uuid import UUID
from pydantic import BaseModel, Field


class CartAdd(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=10000)


class CartQuantity(BaseModel):
    quantity: int = Field(ge=1, le=10000)


class PaymentRequest(BaseModel):
    success: bool = True
