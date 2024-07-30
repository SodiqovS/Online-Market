from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schema
from ecommerce.image import save_image


async def all_users(database: AsyncSession):
    result = await database.execute(select(models.User))
    return result.all()


async def get_user_by_id(user_id, database) -> Optional[models.User]:
    result = await database.execute(select(models.User).filter(models.User.id == user_id))
    user_info = result.scalars().first()
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found !")
    return user_info


async def delete_user_by_id(user_id, database: AsyncSession):
    await database.execute(delete(models.User).filter(models.User.id == user_id))
    await database.commit()
    return {"message": f"<User{user_id}> Deleted Successfully"}


async def edit_profile(request: schema.ProfileUpdate, current_user: models.User, database: AsyncSession):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if request.first_name is not None:
        current_user.first_name = request.first_name
    if request.last_name is not None:
        current_user.last_name = request.last_name
    if request.address is not None:
        current_user.address = request.address

    await database.commit()
    await database.refresh(current_user)

    return {"message": "Profile Updated Successfully"}


async def edit_profile_image(image, current_user: models.User, database):
    image_url = await save_image(image, folder="static/images/users")
    current_user.image = image_url
    await database.commit()
    await database.refresh(current_user)
    return {"message": "Profile Image Updated Successfully"}


async def update_user_by_id(user_id, request, database: AsyncSession):
    user = await get_user_by_id(user_id, database)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await edit_profile(request, user, database)

    if request.is_admin is not None:
        user.is_admin = request.is_admin

    await database.commit()
    await database.refresh(user)
    return {"message": "User Updated Successfully"}
