import datetime
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ecommerce.cart.models import Cart
from ecommerce.db import Base
from ecommerce.orders.models import Order


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(unique=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    is_admin: Mapped[bool] = mapped_column(default=False)

    orders: Mapped[List[Order]] = relationship()

    cart: Mapped[Cart] = relationship()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def __init__(self, first_name, last_name, phone_number, telegram_id, *args, **kwargs):
        super().__init__(**kwargs)
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.telegram_id = telegram_id


# OLD WAY TO CREATE MODEL
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     first_name = Column(String(255), nullable=False)
#     last_name = Column(String(255), nullable=True)
#     phone_number = Column(String(255), unique=True)
#     telegram_id = Column(String(255), unique=True)
#     username = Column(String(255), unique=True, nullable=True)
#     address = Column(String(255), nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#
#     order = relationship("Order", back_populates="user_info")
#     cart = relationship("Cart", back_populates="user_cart")
#
#     is_admin = Column(Boolean, default=False)
#
#     def __str__(self):
#         return f'{self.first_name} {self.last_name}'
#
#     def __init__(self, first_name, last_name, phone_number, telegram_id, *args, **kwargs):
#         super().__init__(**kwargs)
#         self.first_name = first_name
#         self.last_name = last_name
#         self.phone_number = phone_number
#         self.telegram_id = telegram_id
