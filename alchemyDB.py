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
    published = Column(Integer)
    minplayers = Column(Integer)
    maxplayers = Column(Integer)
    suggested_numplayers = Column(Integer) # consider some sort of poll class
    playingtime = Column(Integer)
    minplaytime = Column(Integer)
    maxplaytime = Column(Integer)
    minage = Column(Integer)
    suggested_playerage = Column(Integer)
    language_dependence = Column(Boolean) # consider some sort of poll class

    ## not sure how to handle these many to many in SQL Alchemy
    # category = Column(Integer, ForeignKey('categories.id'))
    # mechanic = ?
    # expansion = ?

    designer = Column(String)
    # artist =
    # publisher =
