import datetime
from typing import List

from pydantic import BaseModel

from ecommerce.products.schema import Product


class ShowCartItems(BaseModel):
    id: int
    products: Product
    quantity: int
    created_date: datetime.datetime

    class Config:
        from_attributes = True


class ShowCart(BaseModel):
    id: int
    cart_items: List[ShowCartItems] = []

    class Config:
        from_attributes = True


class Message(BaseModel):
    msg: str
