import json
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG, filename='missing_img.log', filemode='w+',
                    format='%(message)s')


def get_images(game_json):
    for g in game_json:
        if g['image'] is None:
            id_ = g['id']
            url = f'https://boardgamegeek.com/xmlapi2/thing?id={id_}&type=boardgame&stats=1'
            req = requests.get(url).content
            soup = BeautifulSoup(req, 'xml').find('image')
            if soup is not None:
                g['image'] = soup.text
                print(id_, 'done')
            else:
                logging.DEBUG(f'No image for id: {id_}')
    return game_json


if __name__ == "__main__":
    with open('../data/boardgames.json', 'r') as f:
        data = json.load(f)
    updated_data = get_images(data)
    with open('../data/boardgames+imgs.json', 'w') as f:
        json.dump(updated_data, f)
