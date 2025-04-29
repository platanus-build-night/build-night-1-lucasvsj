# app/models/game.py

from sqlalchemy import (
    Table, Column, Integer, String, Boolean, Date, TIMESTAMP, JSON,
    Numeric, ForeignKey
)
from sqlalchemy.orm import relationship
from app.config.settings import Base

# Junction tables for many-to-many
game_platforms = Table(
    "game_platforms", Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id"), primary_key=True),
    Column("platform_id", Integer, ForeignKey("platforms.id"), primary_key=True)
)

game_developers = Table(
    "game_developers", Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id"), primary_key=True),
    Column("developer_id", Integer, ForeignKey("developers.id"), primary_key=True)
)

game_genres = Table(
    "game_genres", Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True)
)

game_publishers = Table(
    "game_publishers", Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id"), primary_key=True),
    Column("publisher_id", Integer, ForeignKey("publishers.id"), primary_key=True)
)


class ESRBRating(Base):
    __tablename__ = "esrb_ratings"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    games = relationship("Game", back_populates="esrb_rating")


class Platform(Base):
    __tablename__ = "platforms"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    games = relationship("Game", secondary=game_platforms, back_populates="platforms")


class Developer(Base):
    __tablename__ = "developers"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    games = relationship("Game", secondary=game_developers, back_populates="developers")


class Genre(Base):
    __tablename__ = "genres"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    games = relationship("Game", secondary=game_genres, back_populates="genres")


class Publisher(Base):
    __tablename__ = "publishers"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    games = relationship("Game", secondary=game_publishers, back_populates="publishers")


class Game(Base):
    __tablename__ = "games"
    id                  = Column(Integer, primary_key=True, index=True)
    slug                = Column(String, unique=True, nullable=False)
    name                = Column(String, nullable=False)
    metacritic          = Column(Integer)
    released            = Column(Date)
    tba                 = Column(Boolean, default=False)
    updated             = Column(TIMESTAMP)
    website             = Column(String)
    rating              = Column(Numeric)
    rating_top          = Column(Integer)
    playtime            = Column(Integer)
    achievements_count  = Column(Integer)
    ratings_count       = Column(Integer)
    suggestions_count   = Column(Integer)
    game_series_count   = Column(Integer)
    reviews_count       = Column(Integer)
    esrb_rating_id      = Column(Integer, ForeignKey("esrb_ratings.id"))

    # relationships
    esrb_rating   = relationship("ESRBRating", back_populates="games")
    platforms     = relationship("Platform",   secondary=game_platforms,   back_populates="games")
    developers    = relationship("Developer",  secondary=game_developers,  back_populates="games")
    genres        = relationship("Genre",      secondary=game_genres,      back_populates="games")
    publishers    = relationship("Publisher",  secondary=game_publishers,  back_populates="games")

    # Added-status fields
    added_status_yet     = Column(Integer, default=0)
    added_status_owned   = Column(Integer, default=0)
    added_status_beaten  = Column(Integer, default=0)
    added_status_toplay  = Column(Integer, default=0)
    added_status_dropped = Column(Integer, default=0)
    added_status_playing = Column(Integer, default=0)

    # **NEW** one-to-one (or one-to-many) to scraped data
    scraped_data = relationship(
        "GameScrapedData",
        back_populates="game",
        uselist=False,   # one record per game
        cascade="all, delete-orphan"
    )


class GameScrapedData(Base):
    __tablename__ = "game_scraped_data"
    id              = Column(Integer, primary_key=True, index=True)
    game_id         = Column(Integer, ForeignKey("games.id"), unique=True, nullable=False)
    first_paragraph = Column(String)
    image_url       = Column(String)
    infobox         = Column(JSON)

    # relationship back to Game
    game = relationship("Game", back_populates="scraped_data")
