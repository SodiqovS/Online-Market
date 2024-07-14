from typing import Optional

from pydantic import BaseModel, constr


class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    phone_number: Optional[str] = None


class AuthCode(BaseModel):
    code: constr(max_length=6)
