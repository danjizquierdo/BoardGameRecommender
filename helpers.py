import alchemyDB
from collections import defaultdict
from bs4 import BeauitfulSoup as bs


def instantiate_games(xml, id):
    '''
    :param xml: take xml and convert it into a json
    :param id: game id
    :return data: json formatted values for a game
    '''
    soup = bs(xml.content, 'xml')
    data = defaultdict(lambda: 'MissingNaN')
    data['id'] = id
    data['name'] = soup.find('name')['value']
    data['description'] = soup.find('description')
    data['published'] = int(soup.find('yearpublished')['value'])
    data['minplayers'] = int(soup.find('minplayers')['value'])
    data['maxplayers'] = int(soup.find('maxplayers')['value'])
    data['playingtime'] = int(soup.find('playingtime')['value'])
    data['minplaytime'] = int(soup.find('minplaytime')['value'])
    data['maxplaytime'] = int(soup.find('maxplaytime')['value'])
    data['minage'] = int(soup.find('minage')['value'])

    # Loop through polls and save max values
    for poll in soup.find_all('poll'):
        name = poll['name']
        # find the best, recommended, and not recommended player counts
        if name == 'suggested_numplayers':
            suggest ={}
            best=0
            recommended=0
            not_recommended=0
            for results in poll.find_all('results'):
                for result in results.find_all('result'):
                    if result['value']=='Best':
                        if result['numvotes']>best:
                            best = result['numvotes']
                            suggest['best']=results['numplayers']
                    if result['value']=='Recommended':
                        if result['numvotes']>recommended:
                            recommended = result['numvotes']
                            suggest['recommended']=results['numplayers']
                    if result['value']=='Not Recommended':
                        if result['numvotes']>not_recommended:
                            not_recommended = result['numvotes']
                            suggest['not_recommended']=results['numplayers']
            data['best']=suggest['best']
            data['recommended']=suggest['recommended']
            data['not_recommended']=suggest['not_recommended']

            # # refactor to something more like this?
            # for vote in soup.find_all('poll')[0].find_all(attrs={'value': 'Best'}):
            #     vote['numvotes']


    # game = Game(
    #     id=1,
    #     name=soup.find('name')['value'],
    #     description=soup.find('description').text,
    #     published=int(soup.find('yearpublished')['value']),
    #     minplayers=int(soup.find('minplayers')['value']),
    #     maxplayers=int(soup.find('maxplayers')['value']),
    #     # suggested_numplayers,
    #     playingtime=int(soup.find('playingtime')['value']),
    #     minplaytime=int(soup.find('minplaytime')['value']),
    #     maxplaytime=int(soup.find('maxplaytime')['value']),
    #     minage=int(soup.find('minage')['value'])
    # # ,suggested_playerage=,
    # # language_dependence=
    # # ,designer=""
    # mechanics = [Mechanics, Mechanics, Mechanics]
    # )

    return data