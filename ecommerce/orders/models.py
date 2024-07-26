from datetime import datetime
from typing import List

from sqlalchemy import Text, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, mapped_column, Mapped, joinedload

from ecommerce.products.models import Product
from ecommerce.db import Base


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(default=datetime.now)
    order_amount: Mapped[int] = mapped_column(default=0)
    order_status: Mapped[str] = mapped_column(default="PROCESSING")
    shipping_address: Mapped[str] = mapped_column()
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    location: Mapped[str] = mapped_column(nullable=True)

    user_info: Mapped["User"] = relationship("User", back_populates="orders")
    order_details: Mapped[List["OrderDetails"]] = relationship()

    async def load_related(self, database: AsyncSession):
        result = await database.execute(
            select(Order).options(
                joinedload(Order.order_details)
                .joinedload(OrderDetails.product).options(
                    joinedload(Product.images),
                    joinedload(Product.category)
                )
            ).filter(Order.id == self.id)
        )
        return result.scalar()

    def __repr__(self) -> str:
        return f"<Order(id={self.id}>"


class OrderDetails(Base):
    __tablename__ = "order_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('order.id', ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id, ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(default=1)
    created: Mapped[datetime] = mapped_column(default=datetime.now)

    order: Mapped["Order"] = relationship()
    product: Mapped["Product"] = relationship()

    def __repr__(self) -> str:
        return f"<OrderDetails(id={self.id}, order_id={self.order_id}>"
