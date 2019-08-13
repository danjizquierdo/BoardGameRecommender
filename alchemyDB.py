# Code taken from Using an ORM lab
# https://learn.co/tracks/data-science-career-v1-1/module-2-advanced-data-retrieval-and-analysis/section-15-an-introduction-to-orms/using-an-orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import *

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    ratingscount = Column(Integer)
    avgrating = Column(Float)
    published = Column(Integer)
    minplayers = Column(Integer)
    maxplayers = Column(Integer)
    best = Column(Integer)
    recommended = Column(Integer)
    not_recommended = Column(Integer)
    playingtime = Column(Integer)
    minplaytime = Column(Integer)
    maxplaytime = Column(Integer)
    minage = Column(Integer)
    suggestedage = Column(Integer)
    language_dependence = Column(Integer)
    designer = Column(String)
    publisher = Column(String)
    mechanics = relationship('Mechanic', secondary='games_mechanics', back_populates='games')
    categories = relationship('Category', secondary='games_categories', back_populates='games')
    artists = relationship('Artist', secondary='games_artists', back_populates='games')
    # implementations = relationship('Game', secondary='games_implementations', back_populates='games')
    # expansions = relationship('Expansion', secondary='games_expansions', back_populates='games')


class Mechanic(Base):
    __tablename__ = 'mechanics'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    games = relationship('Game', secondary='games_mechanics', back_populates='mechanics')

class Game2Mechanic(Base):
    __tablename__ = 'games_mechanics'
    game_id = Column(Integer, ForeignKey('games.id'), primary_key=True)
    mechanic_id = Column(Integer, ForeignKey('mechanics.id'), primary_key=True)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    games = relationship('Game', secondary='games_categories', back_populates='categories')

class Game2Category(Base):
    __tablename__ = 'games_categories'
    game_id = Column(Integer, ForeignKey('games.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)


class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    games = relationship('Game', secondary='games_artists', back_populates='artists')

class Game2Artist(Base):
    __tablename__ = 'games_artists'
    game_id = Column(Integer, ForeignKey('games.id'), primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), primary_key=True)

# class Implementations(Base):
#     __tablename__ = 'games_implementations'
#     game_id = Column(Integer, ForeignKey('games.id'), primary_key=True)
#     implementation_id = Column(Integer, ForeignKey('games.id'), primary_key=True)

# class Expansion(Base):
#     __tablename__ = 'expansions'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     basegame_id = relationship('Game', ForeignKey('games.id'), back_populates='expansions')

def make_db():
    engine = create_engine('sqlite:///boardgames.db')
    Base.metadata.create_all(engine)
