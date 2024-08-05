import datetime
from typing import Optional

from typing import List
from pydantic import BaseModel

from ecommerce.products.schema import Product


class ShowOrderDetails(BaseModel):
    id: int
    order_id: int
    product: Product

    class Config:
        from_attributes = True


class ShowOrder(BaseModel):
    id: Optional[int]
    order_date: datetime.datetime
    order_amount: float
    order_status: str
    shipping_address: str
    order_details: List[ShowOrderDetails] = []

    class Config:
        from_attributes = True


class OrderRequest(BaseModel):
    shipping_address: Optional[str] = None
