from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, mapped_column, Mapped, joinedload
from ecommerce.db import Base
from ecommerce.products.models import Product


class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_date: Mapped[datetime] = mapped_column(default=datetime.now)

    # user_cart: Mapped["User"] = relationship("User", back_populates="cart", lazy="selectin")
    cart_items: Mapped[List["CartItems"]] = relationship()

    async def load_related(self, database: AsyncSession):
        result = await database.execute(
            select(Cart).options(
                joinedload(Cart.cart_items)
                .joinedload(CartItems.product).options(
                    joinedload(Product.images),
                    joinedload(Product.category)
                )
            )
            .filter(Cart.id == self.id)
        )
        return result.scalar()

    def __repr__(self) -> str:
        return f"<Cart(id={self.id}, user_id={self.user_id})>"


class CartItems(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id, ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(default=1)
    created_date: Mapped[datetime] = mapped_column(default=datetime.now)

    # cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_items", lazy="joined")
    product: Mapped["Product"] = relationship("Product", lazy="joined")

    # async def load_related(self, database: AsyncSession):
    #     result = await database.execute(
    #         select(CartItems).options(
    #             joinedload(Product.images),
    #             joinedload(Product.category)
    #         ).filter(CartItems.id == self.id)
    #     )
    #
    #     return result.scalar()

    def __repr__(self) -> str:
        return f"<CartItems(id={self.id})>"
