import datetime
from typing import Optional, Any

from ecommerce.products.schema import ProductListing

from typing import List, Type, TypeVar
from pydantic import BaseModel


class ShowOrderDetails(BaseModel):
    id: int
    order_id: int
    product: ProductListing

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
