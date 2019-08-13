
from alchemyDB import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///boardgames.db')

Session = sessionmaker(bind=engine)
session = Session()

# how does the data for each game look?


# function to get names of all secondary objects
def names(table):
    return [obj.name for obj in session.query(table).all()]

# function to check if a secondary object exists
def obj_exists(table, name):
    return name in names(table) # boolean

# instantiating the three secondary objects
def instantiate_mechanic(mechanic):
    return Mechanic(name=mechanic)

def instantiate_category(category):
    return Category(name=category)

def instantiate_artist(artist):
    return Artist(name=artist)

def secondary_objects(data):
    relevant_data = None # what keys are relevant?
    # pass thru the checking functions and instantiate

    # checking & instantiating mechanics
    new_mechanics = list(filter(lambda m: obj_exists(Mechanic, m), names(Mechanic)))
    if new_mechanics != []:
        mechanics = [instantiate_mechanic(m) for m in new_mechanics]
    else:
        mechanics = []
    # categories
    new_categories = list(filter(lambda c: obj_exists(Category, c), names(Category)))
    if new_categories != []:
        categories = [instantiate_category(c) for c in new_categories]
    else:
        categories = []
    # artists
    new_artists = list(filter(lambda a: obj_exists(Artist, a), names(Artist)))
    if new_artists != []:
        artists = [instantiate_artist(a) for a in new_artists]
    else:
        artists = []

    return {'mechanics': mechanics, 'categories': categories, 'artists': artists}


# functions to filter all existing secondary objects for names in a list
def findmechanics(m):
    mechanics = []
    for i in m:
        mechanics.extend(session.query(Mechanic).filter(Mechanic.name == i).all())
    return mechanics

def findcategories(c):
    categories = []
    for i in c:
        categories.extend(session.query(Category).filter(Category.name == i).all())
    return categories

def findartists(a):
    artists = []
    for i in a:
        artists.extend(session.query(Artist).filter(Artist.name == i).all())
    return artists

def game_object(data):

    # instantiating secondary objects if they don't yet exist
    new_objects = secondary_objects(data)
    for k, v in new_objects:
        if v != []:
            session.add_all(v)
            session.commit()

    game = Game(name='test',
                description='hi',
                ratingscount=123,
                avgrating=3.5,
                published=1999,
                minplayers=1,
                maxplayers=10,
                suggestednumplayers=6,
                playtime=60,
                minplaytime=30,
                maxplaytime=70,
                minage=4,
                suggestedage=15,
                language_dependensce=2,
                designer='great designer',
                publisher='best publisher',
                )

    game.mechanics = findmechanics(data['mechanics'])
    game.categories = findcategories(data['categories'])
    game.artists = findartists(data['artists'])

    return game





# mechanic1 = Mechanic(name='m1')
# mechanic2 = Mechanic(name='m2')
#
# game1 = Game(name='test',
#             description='hi',
#             ratingscount=123,
#             avgrating=3.5,
#             published=1999,
#             minplayers=1,
#             maxplayers=10,
#             suggestednumplayers=6,
#             playtime=60,
#             minplaytime=30,
#             maxplaytime=70,
#             minage=4,
#             suggestedage=15,
#             language_dependence=2,
#             designer='great designer',
#             publisher='best publisher',
#             mechanics=[mechanic1, mechanic2],
#             categories=[],
#             artists=[]
#             )
#
#
#
# session.add_all([game1, mechanic1, mechanic2])
#
# session.commit()
