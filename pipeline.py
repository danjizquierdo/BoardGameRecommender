from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import pickle
import json

from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.neighbors import NearestNeighbors

eng = create_engine('sqlite:///data/boardgames.db', echo=False)

nn = pickle.load(open('0827test.p', 'rb'))

raw = pd.read_sql_query("SELECT * FROM boardgames", eng).drop(['index', 'designer', 'publisher'], axis=1)

with open('data/boardgames.json') as f:
    game_json = json.load(f)

def preprocess(df):

    relevant = ['id', 'name', 'ratingscount', 'avgrating', 'published',
       'minplayers', 'maxplayers', 'best', 'recommended', 'not_recommended',
       'playingtime', 'minplaytime', 'maxplaytime', 'minage', 'suggestedage',
       'language_dependence']

    outliers = ['published','avgrating','best','maxplayers','maxplaytime','minplaytime','not_recommended','playingtime','ratingscount','recommended']
    normal = ['language_dependence','minage','minplayers','suggestedage']

    df[relevant] = df[relevant].apply(lambda x: x.fillna(x.median()) if x.dtype != np.dtype('O') else x,axis=0)

    robust = RobustScaler()
    df[outliers] = robust.fit_transform(df[outliers])
    minmax = MinMaxScaler()
    df[normal] = minmax.fit_transform(df[normal])

    return df

processed = preprocess(raw)

def dropcols(df):
    to_drop = ['id', 'name', 'description', 'avgrating']
    return df.drop(to_drop, axis=1)

def get_test_array(ids):
    inputs = dropcols(processed[processed['id'].isin(ids)])
    return inputs.mean().values.reshape(1, -1)

def get_nearest(ids, n=5):
    input_array = get_test_array(ids)
    nearest = nn.kneighbors(input_array, n)[-1]
    results = nearest.tolist()[0]
    return results

def get_json(ids, n):
    results = get_nearest(ids)
    return list(filter(lambda g: g['id'] in results and g['id'] not in ids, game_json))

# to get results as a json, just run get_json(LIST_OF_IDS, NUMBER OF RESULTS)
