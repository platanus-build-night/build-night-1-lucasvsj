from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.game import Game, GameScrapedData
from app.config.database import get_session

from app.models.game import Game
from app.config.database import get_session
from app.crud.game import count_games

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def search_games(
    query: str = Query(..., description="Regex to search in game names"),
    ignore_case: bool = Query(True, description="Case-insensitive regex"),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    # Build the SQLAlchemy regex operation
    regex_filter = (
        Game.name.op('~*')(query)
        if ignore_case
        else Game.name.op('~')(query)
    )

    # Total count
    total = await count_games(session, regex_filter)

    # Fetch records with eager loading of relations
    stmt = (
        select(Game)
        .options(
            selectinload(Game.esrb_rating),
            selectinload(Game.platforms),
            selectinload(Game.developers),
            selectinload(Game.genres),
            selectinload(Game.publishers),
            selectinload(Game.scraped_data)
        )
        .where(regex_filter)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    games = result.scalars().all()

    if not games and offset == 0:
        raise HTTPException(status_code=404, detail="No matching games found.")

    # Serialize to dict
    def to_dict(game: Game) -> Dict[str, Any]:
        data = {col.name: getattr(game, col.name) for col in Game.__table__.columns}
        data['esrb_rating'] = (
            {'name': game.esrb_rating.name}
            if game.esrb_rating else None
        )
        data['platforms']  = [{'name': p.name} for p in game.platforms]
        data['developers'] = [{'name': d.name} for d in game.developers]
        data['genres']     = [{'name': g.name} for g in game.genres]
        data['publishers'] = [{'name': p.name} for p in game.publishers]
        if game.scraped_data:
            data['scraped_data'] = {"first_paragraph": game.scraped_data.first_paragraph, "image_url": game.scraped_data.image_url, "infobox": game.scraped_data.infobox}
        return data

    return {"total": total, "results": [to_dict(g) for g in games]}


@router.get(
    "/latest-scraped",
    response_model=Dict[str, Any],
    summary="Get the most recently scraped games"
)
async def latest_scraped_games(
    limit: int = Query(10, ge=1, le=100, description="How many to return"),
    session: AsyncSession = Depends(get_session)
):
    """
    Returns the most recently scraped games (those having a row in `game_scraped_data`),
    ordered by descending scrape‐ID (i.e. newest first).
    """
    # total count of scraped games
    total_q = await session.execute(
        select(func.count()).select_from(GameScrapedData)
    )
    total = total_q.scalar_one()

    # fetch the Game rows
    stmt = (
        select(Game)
        .join(Game.scraped_data)  # only games with scraped_data
        .options(
            selectinload(Game.esrb_rating),
            selectinload(Game.platforms),
            selectinload(Game.developers),
            selectinload(Game.genres),
            selectinload(Game.publishers),
            selectinload(Game.scraped_data),
        )
        .order_by(desc(GameScrapedData.id))
        .limit(limit)
    )
    result = await session.execute(stmt)
    games = result.scalars().all()

    if not games:
        raise HTTPException(
            status_code=404,
            detail="No scraped games found."
        )

    def to_dict(game: Game) -> Dict[str, Any]:
        data = {c.name: getattr(game, c.name) for c in Game.__table__.columns}
        data["esrb_rating"] = (
            {"name": game.esrb_rating.name}
            if game.esrb_rating else None
        )
        data["platforms"] = [{"name": p.name} for p in game.platforms]
        data["developers"] = [{"name": d.name} for d in game.developers]
        data["genres"] = [{"name": g.name} for g in game.genres]
        data["publishers"] = [{"name": p.name} for p in game.publishers]
        # include scraped_data
        sd = game.scraped_data
        data["scraped_data"] = {
            "first_paragraph": sd.first_paragraph,
            "image_url":       sd.image_url,
            "infobox":         sd.infobox,
        }
        return data

    return {"total": total, "results": [to_dict(g) for g in games]}
