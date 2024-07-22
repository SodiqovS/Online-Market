from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .models import Category


async def verify_category_exist(category_id: int, db_session: AsyncSession) -> Optional[Category]:
    result = await db_session.execute(select(models.Category).where(models.Category.id == category_id))
    return result.first()
