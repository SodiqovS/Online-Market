from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ecommerce.auth import schema
from ecommerce.db import get_db
from ecommerce.user import models

SECRET_KEY = "93ua)y!r#k$%0dcojl5u9xr$&9#@w(qh$=fyctcsbg(ms#+hyf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 365


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "token_type": "Bearer"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        token_type: str = payload.get("token_type")
        if phone_number is None:
            raise credentials_exception
        token_data = schema.TokenData(phone_number=phone_number, token_type=token_type)
        return token_data
    except JWTError:
        raise credentials_exception


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.phone_number == token_data.phone_number).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
