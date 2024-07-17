from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import models, schema
from .models import User


async def all_users(database) -> List[models.User]:
    users = database.query(models.User).all()
    return users


async def get_user_by_id(user_id, database) -> Optional[models.User]:
    user_info = database.query(models.User).get(user_id)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found !")
    return user_info


async def delete_user_by_id(user_id, database):
    database.query(models.User).filter(models.User.id == user_id).delete()
    database.commit()


async def edit_profile(request: schema.ProfileUpdate, current_user: User, database: Session):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if request.first_name is not None:
        current_user.first_name = request.first_name
    if request.last_name is not None:
        current_user.last_name = request.last_name
    if request.address is not None:
        current_user.address = request.address

    database.commit()
    database.refresh(current_user)

    return {"message": "Profile Updated Successfully"}


async def update_user_by_id(user_id, request, database):
    user = await get_user_by_id(user_id, database)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await edit_profile(request, user, database)

    if request.is_admin is not None:
        user.is_admin = request.is_admin

    database.commit()
    database.refresh(user)
    return {"message": "User Updated Successfully"}
