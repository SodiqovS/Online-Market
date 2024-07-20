
from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import  AsyncSession
from . import schema
from ecommerce.bot.telegram_bot import bot
from ecommerce import db, redis_config


from .jwt import create_access_token, create_refresh_token, get_auth_user_by_refresh_token

from ecommerce.user.models import User
from .schema import TokenInfo

router = APIRouter(
    tags=['auth']
)


@router.post('/login')
async def login(auth_code: schema.AuthCode, database: AsyncSession = Depends(db.get_db)):
    code = auth_code.code
    telegram_id = redis_config.redis_client.get(code)
    if not telegram_id:
        return {'error': 'Code was expired or invalid'}

    phone_number = redis_config.redis_client.get(telegram_id)
    data = await bot.get_chat(telegram_id)

    user = await database.execute(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        # Foydalanuvchi topilmasa, yangi foydalanuvchi yaratish
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            phone_number=phone_number,
            telegram_id=telegram_id,
            username=data.username,
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
        "user": user,
        "data": TokenInfo(access_token=access_token, refresh_token=refresh_token)
    }

    return response


@router.get('/refresh', response_model=TokenInfo, response_model_exclude_none=True)
async def refresh_access_token(user: User = Depends(get_auth_user_by_refresh_token)):
    access_token = create_access_token(data={"sub": user.phone_number})
    return TokenInfo(access_token=access_token)
