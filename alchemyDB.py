# Code taken from Using an ORM lab
# https://learn.co/tracks/data-science-career-v1-1/module-2-advanced-data-retrieval-and-analysis/section-15-an-introduction-to-orms/using-an-orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    published = Column(int)
    minplayers = Column(int)
    maxplayers = Column(int)
    suggested_numplayers = Column(int) # consider some sort of poll class
    playingtime = Column(int)
    minplaytime = Column(int)
    maxplaytime = Column(int)
    minage = Column(int)
    suggested_playerage = Column(int)
    language_dependence = Column(Boolean) # consider some sort of poll class

    ## not sure how to handle these many to many in SQL Alchemy
    # category = Column(Integer, ForeignKey('categories.id'))
    # mechanic = ?
    # expansion = ?

    designer = Column(String)
    # artist =
    # publisher =

engine = create_engine('sqlite:///games.db')
Base.metadata.create_all(engine)