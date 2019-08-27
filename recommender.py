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
    # Parameter required: game names
    input = request.args.get('games')
    try:
        # Split request into list of strings
        input = input.split(',')
        logging.info(f'Successful request:{input}')
    except:
        logging.error(f'Bad request:{input}')
        abort(400)

    # Perform recommendation
    data = get_nearest(input)
    logging.info(f'Results: {[datum["name"] for datum in data]}')
    logging.info(f'Returned: {data}')

    return {'games': data}

if __name__ == '__main_':
    app.run(debug=True, port=5000)
