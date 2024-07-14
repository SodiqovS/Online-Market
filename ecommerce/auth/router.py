

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from . import schema
from ecommerce.bot.telegram_bot import bot
from ecommerce import db, redis_config


from .jwt import create_access_token, create_refresh_token, verify_token

from ecommerce.user.models import User

router = APIRouter(
    tags=['auth']
)


@router.post('/login')
async def login(auth_code: schema.AuthCode, database: Session = Depends(db.get_db)):
    code = auth_code.code
    telegram_id = redis_config.redis_client.get(code)
    if not telegram_id:
        return {'error': 'Code was expired or invalid'}

    phone_number = redis_config.redis_client.get(telegram_id)
    data = await bot.get_chat(telegram_id)

    user = database.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        # Foydalanuvchi topilmasa, yangi foydalanuvchi yaratish
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            phone_number=phone_number,
            telegram_id=telegram_id,
        )
        database.add(user)
        database.commit()
        database.refresh(user)

    redis_config.redis_client.delete(code)
    redis_config.redis_client.delete(telegram_id)

    access_token = create_access_token(data={"sub": user.phone_number})
    refresh_token = create_refresh_token(data={"sub": user.phone_number})

    response = {
        "message": "User verified successfully",
        "status": status.HTTP_200_OK,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    }

    return response


@router.post('/refresh')
async def refresh_access_token(token: schema.Token, database: Session = Depends(db.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)

    user = database.query(User).filter(User.phone_number == token_data.phone_number).first()

    access_token = create_access_token(data={"sub": user.phone_number})
    return {"access_token": access_token, "token_type": "bearer"}
