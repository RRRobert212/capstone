import re
import pandas as pd

def load_log(filepath):
    return pd.read_csv(filepath)

def create_player_dict(df):
    player_dict = {}
    pattern = r'joined the game'
    for entry in df['entry']:
        match = re.search(pattern, entry)
        if match:
            name = entry.split()[2][1:]
            id = entry.split()[4][:-1]
            player_dict[id] = name
    return player_dict

import re


