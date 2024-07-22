from typing import Optional

from async_lru import alru_cache
from faker import Faker
from fastapi import APIRouter, Depends, status

from fastapi_pagination.ext.sqlalchemy import paginate

from sqlalchemy import select, desc, or_, asc
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce import db
from ecommerce.auth.jwt import get_current_user, get_current_admin
from . import schema
from . import services

from .models import User
from ecommerce.custom_page import CustomPage

router = APIRouter(
    tags=['Users'],
    prefix='/user'
)


@router.get('/fake')
async def fake_data(database: AsyncSession = Depends(db.get_db)):
    fake = Faker()
    for _ in range(100):
        user = User(
            first_name=str(fake.first_name()),
            last_name=str(fake.last_name()),
            phone_number=str(fake.phone_number()),
            telegram_id=str(fake.random_int(1000000, 99999999)),
            username=str(fake.user_name()),
            address=str(fake.address()),
        )
        database.add(user)
        await database.commit()
        await database.refresh(user)
    return {'message': 'Fake successfully'}


@alru_cache()
@router.get('/profile', response_model=schema.DisplayUser)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch('/profile')
async def edit_profile(request: schema.ProfileUpdate,
                       current_user: User = Depends(get_current_user),
                       database: AsyncSession = Depends(db.get_db)):
    return await services.edit_profile(request, current_user, database)


@alru_cache
@router.get('/', response_model=CustomPage[schema.DisplayUser])
async def get_all_users(database: AsyncSession = Depends(db.get_db),
                        s: Optional[str] = None,
                        sort_by: Optional[str] = 'created_at',
                        sort_order: Optional[str] = 'desc',
                        is_admin: Optional[bool] = None,
                        current_admin: User = Depends(get_current_admin)) -> CustomPage[schema.DisplayUser]:
    query = select(User)

    # Search filter
    if s:
        search_filter = or_(
            User.first_name.ilike(f"%{s}%"),
            User.last_name.ilike(f"%{s}%"),
            User.phone_number.ilike(f"%{s}%"),
            User.username.ilike(f"%{s}%")
        )
        query = query.where(search_filter)

    # Admin filter
    if is_admin is not None:
        query = query.where(User.is_admin == is_admin)

    # Sorting
    sort_order_func = {
        'asc': asc,
        'desc': desc
    }

    sort_columns = {
        'id': User.id,
        'created_at': User.created_at,
        'first_name': User.first_name,
        'last_name': User.last_name
    }

    if sort_by in sort_columns and sort_order in sort_order_func:
        query = query.order_by(sort_order_func[sort_order](sort_columns[sort_by]))

    return await paginate(database, query=query)


@router.get('/{user_id}', response_model=schema.DisplayUser)
async def get_user_by_id(user_id: int, database: AsyncSession = Depends(db.get_db),
                         current_admin: User = Depends(get_current_admin)):
    return await services.get_user_by_id(user_id, database)


@router.patch('/{user_id}')
async def patch_user_by_id(user_id: int, request: schema.UserUpdate,
                           database: AsyncSession = Depends(db.get_db),
                           current_admin: User = Depends(get_current_admin)):
    return await services.update_user_by_id(user_id, request, database)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(user_id: int, database: AsyncSession = Depends(db.get_db),
                            current_admin: User = Depends(get_current_admin)):
    return await services.delete_user_by_id(user_id, database)
