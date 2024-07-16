from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr, validator

from ecommerce import db
from . import models


class User(BaseModel):
    first_name: constr(min_length=2, max_length=50)
    last_name: constr(min_length=2, max_length=50)
    phone_number: str
    telegram_id: Optional[int]
    username: Optional[str]

    class Config:
        from_attributes = True


class DisplayUser(BaseModel):
    id: int
    first_name: constr(min_length=2, max_length=50)
    last_name: Optional[str]
    phone_number: str
    telegram_id: Optional[int]
    username: Optional[str]
    created_at: Optional[datetime]
    is_admin: Optional[bool]

    class Config:
        from_attributes = True
