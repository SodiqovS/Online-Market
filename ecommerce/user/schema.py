from typing import Optional

from pydantic import BaseModel, constr, validator

from ecommerce import db
from . import models


class User(BaseModel):
    name: constr(min_length=2, max_length=50)
    email: str
    password: str

    class Config:
        from_attributes = True


class DisplayUser(BaseModel):
    id: int
    name: str
    email: str
    is_admin: Optional[bool]

    class Config:
        from_attributes = True
