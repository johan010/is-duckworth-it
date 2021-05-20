import pandas as pd
from src.utils.utils import over_to_balls, process_match
from ruamel import yaml
from tqdm import tqdm
import os


def load_dls(path_to_csv: str = 'data/DLS table.csv'):
    df_dls = pd.read_csv(path_to_csv)
    df_dls['balls_left'] = df_dls['Overs Left'].apply(over_to_balls)
    return df_dls


def fetch_all_matches(match_type: str = 'ODI') -> pd.DataFrame:
    """Match type options are 'all', 'ODI', 'T20'

    Args:
        match_type (str, optional): match type to get. Defaults to 'ODI'.

    Returns:
        pd.DataFrame: dataframe with all matches ball by ball
    """
    df = pd.DataFrame()
    for yaml_files in tqdm(os.scandir('all_matches')):
        if yaml_files.name.endswith('yaml'):
            with open(yaml_files.path) as f:
                try:
                    my_dict = yaml.safe_load(f)
                    if match_type == 'all':
                        pass
                    elif my_dict['info']['match_type'] != match_type:
                        continue
                    temp_df = process_match(yaml_files.name.split('.')[0], my_dict)
                except Exception as e:
                    print(yaml_files.name.split('.')[0])
                    print(e)
                    continue
            df = pd.concat([df, temp_df])
    return df
