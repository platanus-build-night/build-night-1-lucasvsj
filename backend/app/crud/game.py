from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.game import Game

async def count_games(session: AsyncSession, regex_op) -> int:
    stmt = select(func.count()).select_from(Game).where(regex_op)
    return (await session.execute(stmt)).scalar_one()

async def fetch_games(
    session: AsyncSession,
    regex_op,
    limit: int,
    offset: int
) -> list[Game]:
    stmt = select(Game).where(regex_op).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()