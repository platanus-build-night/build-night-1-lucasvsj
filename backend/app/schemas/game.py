# app/schemas/game.py

from pydantic import BaseModel
from typing   import Optional, List, Dict
from datetime import date

class ScrapedDataOut(BaseModel):
    first_paragraph: Optional[str]
    image_url:       Optional[str]
    infobox:         Optional[Dict[str, List[str]]]  # JSON column

    class Config:
        orm_mode = True


class GameOut(BaseModel):
    id:                   int
    slug:                 str
    name:                 str
    metacritic:           Optional[int]
    released:             Optional[date]
    tba:                  bool
    website:              Optional[str]
    rating:               Optional[float]
    rating_top:           Optional[int]
    playtime:             Optional[int]
    achievements_count:   Optional[int]
    ratings_count:        Optional[int]
    suggestions_count:    Optional[int]
    game_series_count:    Optional[int]
    reviews_count:        Optional[int]
    esrb_rating:          Optional[dict]       # {id:…, name:…}
    platforms:            List[dict]           # list of {id:…, name:…}
    developers:           List[dict]
    genres:               List[dict]
    publishers:           List[dict]

    # **NEW** scraped data
    scraped_data:         Optional[ScrapedDataOut]

    class Config:
        orm_mode = True
