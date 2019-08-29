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

    outliers = ['published','best','maxplayers','maxplaytime','minplaytime','not_recommended','playingtime','ratingscount','recommended']
    normal = ['language_dependence','minage','minplayers','suggestedage','avgrating']

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

def filter_mechanics(mechanics, df = processed):
    ids = []
    for mechanic in mechanics:
        ids.extend(df[df[mechanic] == 1].id.values.tolist())
    return ids

cols = dropcols(processed).columns.tolist()

def featurecloseness(inputs, output):
    # takes in the names of inputs and also results!
    
    invalues = dict(zip(cols, get_test_array(inputs)[0]))
    relevantvals = {k: v for k, v in invalues.items() if v != 0}
    
    output = dropcols(processed[processed['name'] == output]).values.reshape(1, -1)
    outvalues = dict(zip(cols, output[0]))
    outrelevant = {k: outvalues[k] for k in relevantvals.keys()}
    diffdict = {k: abs(outrelevant[k] - relevantvals[k])/relevantvals[k] for k in relevantvals.keys()}
    
    return [r[0] for r in sorted(diffdict.items(), key=lambda kv: kv[1])[:3]]


def get_nearest(names, mechanics, n=100):

    # Grab info for given games
    if names:
        input_array = get_test_array(names)
        # Find the nearest neighbors
        dists, neighbors = nn.kneighbors(input_array, n+len(names))
        dists = dists.tolist()[0]
        neighbors = neighbors.tolist()[0]
        neighborhood = pd.DataFrame(np.array([dists,neighbors]).T,columns=['distance','id'])
        # Scale distances by inverse of avgrating
        weights = processed.query('id == @neighbors')[['id','avgrating']]
        if mechanics:
            # Prefer games with matching mechanics
            mech_games = filter_mechanics(mechanics)
            weights['avgrating'] = weights.apply(lambda x: x['avgrating']*10 if x['id'] in mech_games else x['avgrating'], axis=1)
        # Sort results by new scaled distance
        neighborhood['distance']= pd.merge(neighborhood, weights,on='id').apply(lambda x: x['distance']/(x['avgrating']+.01),axis=1)
        neighborhood.sort_values('distance', inplace=True)
        # Return results not in the given names
        results = list(filter(lambda g: g['name'] not in names, [game_json[int(game_id)] for game_id in list(neighborhood['id'])]))[:3]
        for r in results:
            r['bestfeatures'] = featurecloseness(names, r['name'])
        return results
    elif mechanics:
        # Filters games based on given mechanics
        mech_games = filter_mechanics(mechanics)
        # Finds top 3 rated games with those mechanics
        best_mech = processed.query('id == @mech_games').sort_values('avgrating', ascending=False)['id'].head(3).values
        
        results = list(filter(lambda g: g['bggid'] in best_mech, game_json)).sort(key=lambda g: g['avgrating'], reverse=True)
        
        return results


