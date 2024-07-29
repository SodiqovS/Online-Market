from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi_pagination import paginate
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce import db
from ecommerce.auth.jwt import get_current_user, get_current_admin
from ecommerce.orders.services import initiate_order, get_order_listing, get_all_orders
from ecommerce.user.schema import User
from .schema import ShowOrder
from ..custom_page import CustomPage

router = APIRouter(
    tags=['Orders'],
    prefix='/orders'
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ShowOrder)
async def initiate_order_processing(shipping_address: Optional[str],
                                    current_user: User = Depends(get_current_user),
                                    database: AsyncSession = Depends(db.get_db)):
    result = await initiate_order(current_user, database, shipping_address)
    return result


@router.get('/', status_code=status.HTTP_200_OK, response_model=CustomPage[ShowOrder])
async def orders_list(current_user: User = Depends(get_current_user),
                      database: AsyncSession = Depends(db.get_db)):
    result = await get_order_listing(current_user, database)
    return paginate(result)


@router.get('/all', status_code=status.HTTP_200_OK, response_model=CustomPage[ShowOrder])
async def all_orders(current_admin: User = Depends(get_current_admin),
                     database: AsyncSession = Depends(db.get_db)):
    result = await get_all_orders(database)
    return paginate(result)
