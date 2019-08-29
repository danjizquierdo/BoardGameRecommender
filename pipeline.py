from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import pickle
import json

from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.neighbors import NearestNeighbors

# Load data
eng = create_engine('sqlite:///data/boardgames.db', echo=False)
nn = pickle.load(open('0827test.p', 'rb'))
raw = pd.read_sql_query("SELECT * FROM boardgames", eng).drop(['index', 'designer', 'publisher'], axis=1)

# Open game data
with open('boardgames.json') as f:
    game_json = json.load(f)


def preprocess(df):
    # Perform scaling and grab relevant features
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

# Store processed data for faster retrieval
processed = preprocess(raw)

def dropcols(df):
    # Return only relevant features for KNN
    to_drop = ['id', 'name', 'description', 'avgrating']
    return df.drop(to_drop, axis=1)

def get_test_array(names):
    # Aggregate data for list of names to seed recommendation
    inputs = dropcols(processed[processed['name'].isin(names)])
    return inputs.mean().values.reshape(1, -1)

def get_nearest(names, mechanics, n=10):
    # Grab info for given games
    input_array = get_test_array(names)
    # Find the nearest neighbors
    dists, neighbors = nn.kneighbors(input_array, n+len(names))
    dists = dists.tolist()[0]
    neighbors = neighbors.tolist()[0]
    # Scale distances by inverse of avgrating
    weights = processed.query('id == @neighbors').avgrating
    dists = [dist/(weight+1) for dist, weight in zip(dists, weights)]
    # Sort results by new scaled distance
    dists, neighbors = (list(tup) for tup in zip(*sorted(zip(dists, neighbors))))
    # Return results not in the given names
    return list(filter(lambda g: g['bggid'] in neighbors and g['name'] not in names, game_json))[:5]

# def get_json_by_name(ids, n=10):
#     results = get_nearest(ids, n)
#     return list(filter(lambda g: g['id'] in results and g['id'] not in ids, game_json))

# to get results as a json, just run get_nearest(LIST_OF_MAMES, NUMBER OF RESULTS)


cols = dropcols(processed).columns.tolist()

def featurecloseness(inputs, output):
    # takes in the names of inputs and also results!
    
    invalues = dict(zip(cols, get_test_array(inputs)[0]))
    relevantvals = {k: v for k, v in invalues.items() if v != 0}
    
    output = dropcols(processed[processed['name'] == output]).values.reshape(1, -1)
    
    outvalues = dict(zip(cols, output[0]))
    outrelevant = {k: outvalues[k] for k in relevantvals.keys()}
    diffdict = {k: abs(outrelevant[k] - relevantvals[k]) for k in relevantvals.keys()}
    
    return {'features': [r[0] for r in sorted(diffdict.items(), key=lambda kv: kv[1])[:3]]}

