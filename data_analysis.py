#%%
import pandas as pd
import json

#%%
max_pair_scores = None
pairs_made = None
pairs_declined = None
opt_outs = None

with open('dyadica_data.json', 'r') as f:
    data = json.load(f)
    max_pair_scores = pd.read_json(data['max_pair_scores'])
    pairs_made = pd.Series(data["pairs_made"])
    pairs_declined = pd.Series(data["pairs_declined"])
    opt_outs = pd.Series(data['opt_outs'])


# %%
