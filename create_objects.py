from alchemyDB import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import defaultdict
from bs4 import BeautifulSoup as bs
import re
from operator import itemgetter

engine = create_engine('sqlite:///boardgames.db')

Session = sessionmaker(bind=engine, autoflush=False)
session = Session()


# how does the data for each game look?


# function to get names of all secondary objects
# to map the strings in game data to objects
def names(table):
	return [obj.name for obj in session.query(table).all()]


# function to check if a secondary object exists
def obj_exists(table, name):
	return name not in names(table)  # boolean


# instantiating the three secondary objects
def instantiate_mechanic(mechanic):
	return Mechanic(name=mechanic)


def instantiate_category(category):
	return Category(name=category)


def instantiate_artist(artist):
	return Artist(name=artist)


def secondary_objects(data):

	mechanics = data['mechanics']
	categories = data['categories']
	artists = data['artists']
	# pass thru the checking functions and instantiate

	# checking & instantiating mechanics
	new_mechanics = list(filter(lambda m: obj_exists(Mechanic, m), mechanics))
	if new_mechanics != []:
		mechanics_obj = [instantiate_mechanic(m) for m in new_mechanics]
	else:
		mechanics_obj = []
	# categories
	new_categories = list(filter(lambda c: obj_exists(Category, c), categories))
	if new_categories != []:
		categories_obj = [instantiate_category(c) for c in new_categories]
	else:
		categories_obj = []
	# artists
	new_artists = list(filter(lambda a: obj_exists(Artist, a), artists))
	if new_artists != []:
		artists_obj = [instantiate_artist(a) for a in new_artists]
	else:
		artists_obj = []

	return {'mechanics': mechanics_obj, 'categories': categories_obj, 'artists': artists_obj}


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


def strip_values(int_like):
	# XML attributes from Str -> Int
	try:
		return int(int_like)
	except ValueError:
		return int(re.search(r'\d+', int_like).group()) + 1


def instantiate_games(req):
	""""
	:param req: XML request to parse
	:return data: Game object
	"""
	soup = bs(req.content, 'xml')
	data = defaultdict(lambda: -100)  # value it could never be
	data['id'] = int(soup.find('item')['id'])
	data['name'] = soup.find('name')['value']
	data['description'] = soup.find('description').text
	data['ratingscount'] = int(soup.find('usersrated')['value'])
	data['avgrating'] = float(soup.find('bayesaverage')['value'])
	data['published'] = int(soup.find('yearpublished')['value'])
	data['minplayers'] = int(soup.find('minplayers')['value'])
	data['maxplayers'] = int(soup.find('maxplayers')['value'])

	# Loop through polls and save max values
	for poll in soup.find_all('poll'):
		name = poll['name']

		# find the best, recommended, and not recommended player counts
		if name == 'suggested_numplayers':
			players = [strip_values(results['numplayers']) for results in poll.find_all('results')]
			best = [int(vote['numvotes']) for vote in poll.find_all('result', value='Best')]
			recommended = [int(vote['numvotes']) for vote in poll.find_all('result', value='Recommended')]
			not_recommended = [int(vote['numvotes']) for vote in poll.find_all('result', value='Not Recommended')]

			data['best'] = players[best.index(max(best))]
			data['recommended'] = players[recommended.index(max(recommended))]
			data['not_recommended'] = players[not_recommended.index(max(not_recommended))]

		# find the suggested player age
		if name == 'suggested_playerage':
			suggestedage = [(strip_values(vote['value']), int(vote['numvotes'])) for vote in poll.find_all('result')]
			data['suggestedage'] = max(suggestedage, key=itemgetter(1))[0]

		# find the language skill necessary to play: 1 is low, 5 is high
		if name == 'language_dependence':
			language_dependence = [(int(vote['level']), int(vote['numvotes'])) for vote in poll.find_all('result')]
			data['language_dependence'] = max(language_dependence, key=itemgetter(1))[0]

	data['playingtime'] = int(soup.find('playingtime')['value'])
	data['minplaytime'] = int(soup.find('minplaytime')['value'])
	data['maxplaytime'] = int(soup.find('maxplaytime')['value'])
	data['minage'] = int(soup.find('minage')['value'])
	data['designer'] = soup.find('link', type='boardgamedesigner')['value']
	data['publisher'] = soup.find('link', type='boardgamepublisher')['value']

	# # connect to DB and check for category, mechanic, expansions, implementations, artist
	rel = {}
	rel['categories'] = [result['value'] for result in soup.find_all('link', type='boardgamecategory')]
	rel['mechanics'] = [result['value'] for result in soup.find_all('link', type='boardgamemechanic')]
	rel['artists'] = [result['value'] for result in soup.find_all('link', type='boardgameartist')]
	# soup.find('link',type='boardgameexpansion')['value']
	# soup.find('link',type='boardgameimplementation')['value']

	new_objects = secondary_objects(rel)

	for k, v in new_objects.items():
		if v != []:
			session.add_all(v)
			session.commit()

	game = Game(**data)
	game.mechanics = findmechanics(rel['mechanics'])
	game.categories = findcategories(rel['categories'])
	game.artists = findartists(rel['artists'])

	try:
		session.add(game)
		session.commit()
		return True
	except:
		print(f'Something went wrong with game {data["id"]}')
		session.rollback()
		return False


def rollback():
	session.rollback()


def get_game_collection():
	return len(session.query(Game).all())

# def game_object(data):
#     # instantiating secondary objects if they don't yet exist
#     new_objects = secondary_objects(data)
#     for k, v in new_objects:
#         if v != []:
#             session.add_all(v)
#             session.commit()
#
#     game.mechanics = findmechanics(data['mechanics'])
#     game.categories = findcategories(data['categories'])
#     game.artists = findartists(data['artists'])
#
#     return game

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
