from typing import List

from fastapi import APIRouter, Depends, status, Response, HTTPException

from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from fastapi_filters.ext.sqlalchemy import apply_filters
from fastapi_filters import create_filters, create_filters_from_model, FilterValues

from sqlalchemy import select
from sqlalchemy.orm import Session

from ecommerce import db
from ecommerce.auth.jwt import get_current_user, get_current_admin
from . import schema
from . import services
from . import validator
from .models import User

router = APIRouter(
    tags=['Users'],
    prefix='/user'
)


# Interesting Question for Global Dependency
# https://github.com/tiangolo/fastapi/issues/2481


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user_registration(request: schema.User, database: Session = Depends(db.get_db)):
    # Read More : Pydantic Validation with Database (https://github.com/tiangolo/fastapi/issues/979)

    user = await validator.verify_email_exist(request.email, database)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this phone already exists in the system.",
        )

    new_user = await services.new_user_register(request, database)
    return new_user


@router.get('/', response_model=Page[schema.DisplayUser])
async def get_all_users(database: Session = Depends(db.get_db),
                        filters: FilterValues = Depends(create_filters_from_model(schema.DisplayUser)),
                        current_admin: schema.User = Depends(get_current_admin)) -> Page[schema.DisplayUser]:
    query = apply_filters(select(schema.DisplayUser), filters)
    return paginate(database, query)


@router.get('/{user_id}', response_model=schema.DisplayUser)
async def get_user_by_id(user_id: int, database: Session = Depends(db.get_db),
                         current_admin: schema.User = Depends(get_current_admin)):
    return await services.get_user_by_id(user_id, database)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_user_by_id(user_id: int, database: Session = Depends(db.get_db),
                            current_user: schema.User = Depends(get_current_user)):
    return await services.delete_user_by_id(user_id, database)
