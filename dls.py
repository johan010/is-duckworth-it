import pandas as pd
from ruamel import yaml
import numpy as np
import os
from tqdm import tqdm

def get_wickets(rows):
    if type(rows) == float:
        return {'player_out': np.nan, 'fielders': np.nan, 'kind': np.nan}
    elif (len(rows.keys())) == 2:
        return {'player_out': rows['player_out'], 'fielders': np.nan, 'kind': rows['kind']}
    else:
        return rows

def get_bat_first(rows):
    if (rows['team_1'] == rows['toss_winner']) & (rows['toss_decision'] == 'bat'):
        return rows['team_1']
    elif (rows['team_2'] == rows['toss_winner']) & (rows['toss_decision'] == 'field'):
        return rows['team_1']
    else:
        return rows['team_2']


def process_match(match_id, diction):
    new_df = pd.DataFrame()
    for idx, ins in enumerate(['1st innings', '2nd innings']):
        if (len(diction['innings'][0]) == 1) & (ins == '2nd innings'):
            continue
        df = pd.DataFrame([x.values() for x in diction['innings'][idx][ins]['deliveries']])
        df['over'] = pd.DataFrame([x.keys() for x in diction['innings'][idx][ins]['deliveries']])
        df['ins'] = ins
        df = df.merge(pd.DataFrame([x for x in df[0]]), left_index=True, right_index=True)
        df = df.merge(pd.DataFrame([x for x in df['runs']]), left_index=True, right_index=True)
        if 'extras_x' not in df.columns:
            df['extras_x'] = df['extras']
            df['extras_type'] = np.nan
            df['extras_amount'] = 0
            df['extras_y'] = np.nan
        else:
            df['extras_type'] = df['extras_x'].apply(lambda x:list( x.keys())[0] if type(x) != float else np.nan)
            df['extras_amount'] = df['extras_y']
        df['batsman_runs'] = df['batsman_y']
        if 'wicket' in df.columns:
            df = df.merge(df['wicket'].apply(get_wickets).apply(lambda x  : pd.Series({ k: v for k, v in x.items() })), left_index=True, right_index=True)
        else:
            df['wicket'] = 0.0
            df = df.merge(df['wicket'].apply(get_wickets).apply(lambda x  : pd.Series({ k: v for k, v in x.items() })), left_index=True, right_index=True)
        df = df.drop(['wicket', 'batsman_y', 'extras_x', 'extras_y', 0, 'runs'], axis=1)
        new_df = pd.concat([new_df, df])
    if 'city' in diction['info'].keys():
        new_df['city'] = diction['info']['city']
    else: new_df['city'] = 'unspecified'
    if 'competition' in diction['info'].keys():
        new_df['competition'] = diction['info']['competition']
    else:
        new_df['competition'] = np.nan
    new_df['dates'] = str(diction['info']['dates'])
    new_df['gender'] = diction['info']['gender']
    new_df['match_type'] = diction['info']['match_type']
    if 'winner' in diction['info']['outcome'].keys(): 
        new_df['winner'] = diction['info']['outcome']['winner']
        new_df['winner_method'] = list(diction['info']['outcome']['by'].keys())[0]
        new_df['winner_amount'] = list(diction['info']['outcome']['by'].values())[0]
    elif 'result' in diction['info']['outcome'].keys(): 
         new_df['winner'] = diction['info']['outcome']['result']
         new_df['winner_method'] = np.nan
         new_df['winner_amount'] = np.nan
    if 'overs' in diction['info'].keys():
        new_df['overs'] = diction['info']['overs']
    else:
        new_df['overs'] = 'test_match'
    if 'player_of_match' in diction['info'].keys():
        new_df['player_of_match'] = diction['info']['player_of_match'][0]
    else: new_df['player_of_match'] = np.nan
    new_df['team_1'] = diction['info']['teams'][0]
    new_df['team_2'] = diction['info']['teams'][1]
    new_df['toss_winner'] = diction['info']['toss']['winner']
    new_df['toss_decision'] = diction['info']['toss']['decision']
    if 'umpires' in diction['info'].keys():
        new_df['umpire_1'] = diction['info']['umpires'][0]
        new_df['umpire_2'] = diction['info']['umpires'][1]
    else:
        new_df['umpire_1'] = np.nan
        new_df['umpire_2'] = np.nan
    new_df['venue'] = diction['info']['venue']
    new_df['team_bat_first'] = new_df.apply(get_bat_first, axis=1)
    new_df['match_id'] = match_id
    return new_df



def recources_remaining_odi(balls_left, w_left, team_one_score,df_dls):
    """This is for ODI's only where there were no reduction in overs

    Args:
        balls_left ([type]): [description]
        w_left ([type]): [description]
        team_one_score ([type]): [description]
        df_dls ([type]): [description]
    """
    print("test")


df = pd.DataFrame()
for yaml_files in tqdm(os.scandir('all_matches')):
    if yaml_files.name.endswith('yaml'):
        with open(yaml_files.path) as f:
            try:
               
                my_dict = yaml.safe_load(f)
                temp_df = process_match(yaml_files.name.split('.')[0], my_dict)
            except Exception as e:
                 print(yaml_files.name.split('.')[0])
                 print(e)
                 continue
        df = pd.concat([df, temp_df])

# test_file = '/home/johan/Documents/cric/all_matches/1158359.yaml'
# with open(test_file) as f:
#     my_dict = yaml.safe_load(f)
# new_df = pd.DataFrame()
# for idx, ins in enumerate(['1st innings', '2nd innings']):
#     df = pd.DataFrame([x.values() for x in my_dict['innings'][idx][ins]['deliveries']])
#     df['over'] = pd.DataFrame([x.keys() for x in my_dict['innings'][idx][ins]['deliveries']])
#     df['ins'] = ins
#     df = df.merge(pd.DataFrame([x for x in df[0]]), left_index=True, right_index=True)
#     df = df.merge(pd.DataFrame([x for x in df['runs']]), left_index=True, right_index=True)

# new_df = process_match(my_dict)
# pd.DataFrame(my_dict['info'])
# my_dict['info']
# my_dict['info']
# new_df = new_df['wicket'].reset_index()
# new_df[new_df['wicket'].values != np.nan]



# new_df['wicket'].apply(get_wickets).apply(lambda x  : pd.Series({ k: v for k, v in x.items() }))

