# products/models.py

from typing import List
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from ecommerce.db import Base


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="category", lazy="select")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="images", lazy="select")

    def __repr__(self) -> str:
        return f"<Image(id={self.id}, url={self.url})>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))

    category: Mapped["Category"] = relationship("Category", back_populates="products", lazy="select")
    images: Mapped[List["Image"]] = relationship("Image", back_populates="product", lazy="select")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, category_id={self.category_id})>"
