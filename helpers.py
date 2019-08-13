from alchemyDB import *
from collections import defaultdict
from bs4 import BeautifulSoup as bs
import re
from operator import itemgetter


def strip_values(int_like):
	# XML attributes from Str -> Int
	try:
		return int(int_like)
	except ValueError:
		return int(re.search(r'\d+', int_like).group())+1


def instantiate_games(xml):
	""""
	:param xml: XML data to parse
	:return data: Game object
	"""
	soup = bs(xml.content, 'xml')
	data = defaultdict(lambda: 'MissingNaN')
	data['id'] = int(soup.find('item')['id'])
	data['name'] = soup.find('name')['value']
	data['description'] = soup.find('description').text
	data['ratingscount'] = soup.find('usersrated')['value']
	data['avgrating'] = soup.find('bayesaverage')['value']
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

			data['best']=players[best.index(max(best))]
			data['recommended']=players[recommended.index(max(recommended))]
			data['not_recommended']=players[not_recommended.index(max(not_recommended))]

		# find the suggested player age
		if name == 'suggested_playerage':
			suggestedage = [(strip_values(vote['value']), int(vote['numvotes'])) for vote in poll.find_all('result')]
			data['suggestedage'] = max(suggestedage, key = itemgetter(1))[0]

		# find the language skill necessary to play: 1 is low, 5 is high
		if name == 'language_dependence':
			language_dependence = [(int(vote['level']), int(vote['numvotes'])) for vote in poll.find_all('result')]
			data['language_dependence'] = max(language_dependence, key = itemgetter(1))[0]

	data['playingtime'] = int(soup.find('playingtime')['value'])
	data['minplaytime'] = int(soup.find('minplaytime')['value'])
	data['maxplaytime'] = int(soup.find('maxplaytime')['value'])
	data['minage'] = int(soup.find('minage')['value'])
	data['designer'] = soup.find('link', type='boardgamedesigner')['value']
	data['publisher'] = soup.find('link', type='boardgamepublisher')['value']

	# # connect to DB and check for category, mechanic, expansions, implementations, artist
	# soup.find('link',type='boardgamecategory')['value']
	# soup.find('link',type='boardgamemechanic')['value']
	# soup.find('link',type='boardgameexpansion')['value']
	# soup.find('link',type='boardgameimplementation')['value']
	# soup.find('link',type='boardgameartist')['value']

	# game = Game(data) ?

	return data

# def instantiate_mechanic(name):
# 	# Search database for given mechanic name
# 	# if exists, return object
# 	# else create and return object

# def instantiate_category(name):
# 	# Search database for given category name
# 	# if exists, return object
# 	# else create and return object

# def instantiate_artist(name):
# 	# Search database for given artist name
# 	# if exists, return object
# 	# else create and return object

# def instantiate_implementation(id):
# 	# Search database for given game
# 	# if exists, return object
# 	# else search for implementation in API, create and return object

# def instantiate_expansion(name):
# 	# Search database for given expansion
# 	# if exists, return object
# 	# else search for implementation in API, create and return object
