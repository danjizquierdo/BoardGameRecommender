import os
import time
import logging

from pipeline import *
import requests
from flask import abort, Flask, request
from flask_cors import CORS, cross_origin
# from zappa.async import task

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w+', format='%(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)


# def is_request_valid(request):
#     is_token_valid = request.args.get('passphrase') == 'learnlovecode'
#
#     return is_token_valid

@app.route('/rec', methods=['POST'])
def find_games():
    try:
        # Parameter options: game names or mechanic names
        params=dict()
        params['games'] = request.args.get('games')
        params['mechanics'] = request.args.get('mechanics')
        # Split request into list of strings
        games = params['games'].split(',') if params['games'] else []
        # Split request into list of strings
        mechanics = params['mechanics'].split(',') if params['mechanics'] else []
        logging.info(f'Successful request: \n Games: {games if games else "None"} \n Mechanics: {mechanics if mechanics else "None"}')
    except:
        logging.error(f'Bad request: {request}')
        abort(400)

    # Perform recommendation
    data = get_nearest(games,mechanics)
    logging.info(f'Results: {[datum["name"] for datum in data]}')
    line = '\n'
    logging.info(f'Returned: {line}{line.join([str(datum)+line for datum in data])}')

    return {'games': data}

if __name__ == '__main_':
    app.run(host='0.0.0.0', port=80)
