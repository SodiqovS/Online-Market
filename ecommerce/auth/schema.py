from typing import Optional, Union

from pydantic import BaseModel, constr


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: Union[str, None] = None
    token_type: str = "Bearer"


class TokenData(BaseModel):
    phone_number: Optional[str] = None
    user_id: Optional[int] = None
    token_type: Optional[str] = None


class AuthCode(BaseModel):
    code: constr(min_length=6, max_length=6)
