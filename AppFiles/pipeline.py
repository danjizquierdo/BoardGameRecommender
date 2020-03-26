from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import pickle
import json
from operator import itemgetter
from sklearn.preprocessing import MinMaxScaler, QuantileTransformer
from sklearn.neighbors import NearestNeighbors

# Load raw data
eng = create_engine('sqlite:///data/boardgames.db', echo=False)
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
    # Separate features in terms of appropriate scaling
    outliers = ['published', 'best', 'maxplayers', 'maxplaytime', 'minplaytime', 'not_recommended', 'playingtime',
                'ratingscount', 'recommended']
    normal = ['language_dependence', 'minage', 'minplayers', 'suggestedage', 'avgrating']

    # Fill missing values with the median
    df[relevant] = df[relevant].apply(lambda x: x.fillna(x.median()) if x.dtype != np.dtype('O') else x, axis=0)

    # Perform robust scaling by transforming to normal distribution and then within 0-1 range
    robust = QuantileTransformer()
    minmax = MinMaxScaler()
    df[outliers] = minmax.fit_transform(robust.fit_transform(df[outliers]))
    # Perform linear transformation to normally distributed features
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


def filter_mechanics(mechanics, df=processed):
    # Filter out games that do not contain the given mechanics
    ids = set()
    for mechanic in mechanics:
        ids.add(df[df[mechanic] == 1].id.values.tolist())

    return list(ids)


# Get only the relevant column names for feature comparisons
cols = dropcols(processed).columns.tolist()


def feature_closeness(inputs, output):
    # Takes in the names of inputs and results to determine which features were most relevant for recommendations
    invalues = dict(zip(cols, get_test_array(inputs)[0]))
    relevantvals = {k: v for k, v in invalues.items() if v != 0}
    
    output = dropcols(processed[processed['name'] == output]).values.reshape(1, -1)
    outvalues = dict(zip(cols, output[0]))
    outrelevant = {k: outvalues[k] for k in relevantvals.keys()}
    diffdict = {k: abs(outrelevant[k] - relevantvals[k])/relevantvals[k] for k in relevantvals.keys()}
    
    return [r[0] for r in sorted(diffdict.items(), key=lambda kv: kv[1])[:3]]


def store_mvp(data, *filename):
    # Creates and returns MVP Nearest Neighbors model to use for recommendations
    model = NearestNeighbors(n_neighbors=5)
    model.fit(dropcols(preprocess(data)))
    # Saves file if a filename was given
    if filename:
        pickle.dump(model, open(f'{filename}.p', 'wb'))
    return model


def get_nearest(names, mechanics, n=100):
    # Grab info for given games if games were given
    if names:
        # Set up inputs
        input_array = get_test_array(names)
        # Find the nearest neighbors
        dists, neighbors = nn.kneighbors(input_array, n+len(names))
        dists = dists.tolist()[0]
        neighbors = neighbors.tolist()[0]
        neighborhood = pd.DataFrame(np.array([dists, neighbors]).T, columns=['distance', 'id'])
        # Grab avgrating for each game to be used as weighting factor
        weights = processed.query('id == @neighbors')[['id', 'avgrating']]
        # If mechanics were given, bias towards games with matching mechanics
        if mechanics:
            # Prefer games with matching mechanics by adjusting their avgrating
            mech_games = filter_mechanics(mechanics)
            weights['avgrating'] = weights.apply(
                lambda x: x['avgrating']*10 if x['id'] in mech_games else x['avgrating'], axis=1)
        # Scale distances by inverse of avgrating, bias towards higher rated games. Sort results by new scaled distance
        neighborhood['distance'] = pd.merge(neighborhood, weights, on='id').apply(
            lambda x: x['distance']/(x['avgrating']+.01), axis=1)
        # Make sure id is correct dtype
        neighborhood['id'] = neighborhood['id'].apply(int)
        neighborhood.sort_values('distance', inplace=True)
        # Return results not in the given names
        results = []
        for idx in neighborhood['id'].tolist():
            if game_json[idx]['name'] not in names:
                results.append(game_json[idx])
        # Find what results were most impactful in the recommendation decision
        for r in results:
            r['bestfeatures'] = feature_closeness(names, r['name'])
    # If only mechanics were given, sort out games without those mechanics and recommend top games
    elif mechanics:
        # Filters games based on given mechanics
        mech_games = filter_mechanics(mechanics)
        # Finds top 3 rated games with those mechanics
        if mech_games:
            best_mech = processed.query('id == @mech_games').sort_values('avgrating',
                                                                         ascending=False)['id'].head(3).values
        # If there are no games with all of the given mechanics, go through each individually
        else:
            print('No mech_games')
            best_mech = processed.sort_values('avgrating',ascending=False)['id'].head(3).values
        results = sorted(list(filter(lambda g: g['bggid'] in best_mech.tolist(), game_json)),
                         key=lambda g: g['avgrating'], reverse=True)
    return results[:3]


if __name__ == "__main__":
    # If run as a script, create a NearestNeighbors model with the passed in BG data and save.
    nn = store_mvp(raw)
else:
    # Otherwise load up pre-existing model
    nn = pickle.load(open('BGGuru.p', 'rb'))
