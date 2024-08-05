from typing import List

from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, mapped_column, Mapped, joinedload
from ecommerce.db import Base


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    image_url: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"<Image(id={self.id}, url={self.url})>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    sold_quantity: Mapped[int] = mapped_column(Integer, default=0)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))

    category: Mapped[Category] = relationship()
    images: Mapped[List[Image]] = relationship()

    async def load_related(self, database: AsyncSession):
        result = await database.execute(
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.images)
            )
            .filter(Product.id == self.id)
        )
        return result.scalar()

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, category_id={self.category_id})>"
