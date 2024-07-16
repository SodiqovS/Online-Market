from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from ecommerce.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    phone_number = Column(String(255), unique=True)
    telegram_id = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="user_info")
    cart = relationship("Cart", back_populates="user_cart")

    is_admin = Column(Boolean, default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def __init__(self, first_name, last_name, phone_number, telegram_id, *args, **kwargs):
        super().__init__(**kwargs)
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.telegram_id = telegram_id
