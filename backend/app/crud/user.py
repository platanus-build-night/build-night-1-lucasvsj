from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import verify_password, get_password_hash

async def get_user_by_username(session: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    return (await session.execute(stmt)).scalar_one_or_none()

async def create_user(
    session: AsyncSession,
    username: str,
    email: str,
    password: str
) -> User:
    hashed = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str
) -> User | None:
    user = await get_user_by_username(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user