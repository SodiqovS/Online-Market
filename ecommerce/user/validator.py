from typing import Optional

from sqlalchemy.ext.asyncio import  AsyncSession

from .models import User


async def verify_email_exist(email: str, db_session: AsyncSession) -> Optional[User]:
    return db_session.query(User).filter(User.email == email).first()
