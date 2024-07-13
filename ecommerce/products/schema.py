from pydantic import BaseModel, constr
from typing import List, Optional


class Image(BaseModel):
    id: Optional[int]
    url: str

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class ListCategory(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    name: str
    quantity: int
    description: str
    price: float
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[constr(min_length=2, max_length=50)]
    quantity: Optional[int]
    description: Optional[str]
    price: Optional[float]
    category_id: Optional[int]


class Product(ProductBase):
    id: int
    images: List[Image] = []

    class Config:
        orm_mode = True


class ProductListing(Product):
    category: ListCategory

    class Config:
        orm_mode = True


class ProductPaging(BaseModel):
    products: List[ProductListing]
    total_products: int
    total_pages: int
    current_page: int
