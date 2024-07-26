from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import schema
from ecommerce.bot.telegram_bot import bot
from ecommerce import db, redis_config
from .jwt import create_access_token, create_refresh_token, get_auth_user_by_refresh_token
from ecommerce.user.models import User
from .schema import TokenInfo

router = APIRouter(tags=['auth'])


@router.post('/login')
async def login(auth_code: schema.AuthCode, database: AsyncSession = Depends(db.get_db)):
    code = auth_code.code
    telegram_id = redis_config.redis_client.get(code)
    if not telegram_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code was expired or invalid")

    phone_number = redis_config.redis_client.get(telegram_id)
    data = await bot.get_chat(telegram_id)

    result = await database.execute(select(User).filter(User.phone_number == phone_number))
    user = result.scalar_one_or_none()

    if not user:
        # Create new user if not found
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            phone_number=phone_number,
            telegram_id=telegram_id,
            username=data.username,
        )
        database.add(user)
        await database.commit()
        await database.refresh(user)

    redis_config.redis_client.delete(code)
    redis_config.redis_client.delete(telegram_id)

    data = {"sub": user.phone_number, "user_id": user.id}

    access_token = await create_access_token(data)
    refresh_token = await create_refresh_token(data)

    response = {
        "message": "User verified successfully",
        "status": status.HTTP_200_OK,
        "user": user,
        "data": TokenInfo(access_token=access_token, refresh_token=refresh_token)
    }

    return response


@router.get('/refresh', response_model=TokenInfo, response_model_exclude_none=True)
async def refresh_access_token(user: User = Depends(get_auth_user_by_refresh_token)):
    access_token = await create_access_token(data={"sub": user.phone_number, "user_id": user.id})
    return TokenInfo(access_token=access_token)
