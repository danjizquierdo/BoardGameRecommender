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
with open('data.json') as f:
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

def get_nearest(names, mechanics, n=20):
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
            weights.apply(lambda x: x['avgrating']*10 if x['id'] in mech_games else x['avgrating'],axis=1)
        # Sort results by new scaled distance
        neighborhood['distance']= pd.merge(neighborhood,weights,on='id').apply(lambda x: x['distance']/(x['avgrating']+.01),axis=1)
        neighborhood.sort_values('distance',inplace=True)
        # Return results not in the given names
        return list(filter(lambda g: g['name'] not in names, [game_json[int(game_id)] for game_id in list(neighborhood['id'])]))[:5]
    elif mechanics:
        # Filters games based on given mechanics
        mech_games = filter_mechanics(mechanics)
        # Finds top 3 rated games with those mechanics
        best_mech = processed.query('id == @mech_games').sort_values('avgrating', ascending=False)['id'].head(3).values
        return list(filter(lambda g: g['id'] in best_mech, game_json))
