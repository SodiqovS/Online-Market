from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, constr


class User(BaseModel):
    first_name: constr(min_length=2, max_length=50)
    last_name: Optional[str]
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
    address: Optional[str]
    is_admin: Optional[bool]

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    address: Union[str, None] = None


class UserUpdate(ProfileUpdate):
    is_admin: Union[bool, None] = None

