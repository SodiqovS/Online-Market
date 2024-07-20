
from datetime import datetime
from typing import List
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from ecommerce.products.models import Product
from ecommerce.db import Base


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(default=datetime.now)
    order_amount: Mapped[int] = mapped_column(default=0)
    order_status: Mapped[str] = mapped_column(String, default="PROCESSING")
    shipping_address: Mapped[str] = mapped_column(Text)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user_info: Mapped["User"] = relationship("User", back_populates="orders")
    order_details: Mapped[List["OrderDetails"]] = relationship("OrderDetails", back_populates="order")

    def __repr__(self) -> str:
        return f"<Order(id={self.id}>"


class OrderDetails(Base):
    __tablename__ = "order_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('order.id', ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id, ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(default=1)
    created: Mapped[datetime] = mapped_column(default=datetime.now)

    order: Mapped["Order"] = relationship("Order", back_populates="order_details", lazy="select")
    product_order_details: Mapped["Product"] = relationship("Product", lazy="select")

    def __repr__(self) -> str:
        return f"<OrderDetails(id={self.id}, order_id={self.order_id}>"
