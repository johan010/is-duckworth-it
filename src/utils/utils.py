import pandas as pd
import numpy as np
from tqdm import tqdm

def over_to_balls(over):
    over = str(over)
    overs = int(over.split('.')[0])
    balls = int(over.split('.')[1])
    return overs * 6 + balls

def is_dead_ball(extras):
    if extras in ['wides', 'noballs']:
        return True
    else:
        return False

def get_bat_first(rows):
    if (rows['team_1'] == rows['toss_winner']) & (rows['toss_decision'] == 'bat'):
        return rows['team_1']
    elif (rows['team_2'] == rows['toss_winner']) & (rows['toss_decision'] == 'field'):
        return rows['team_1']
    else:
        return rows['team_2']

def get_wickets(rows):
    if type(rows) == float:
        return {'player_out': np.nan, 'fielders': np.nan, 'kind': np.nan}
    elif (len(rows.keys())) == 2:
        return {'player_out': rows['player_out'], 'fielders': np.nan, 'kind': rows['kind']}
    else:
        return rows

def get_current_runs(df_match):
    for ins in ['1st innings', '2nd innings']:
        temps = pd.DataFrame(
            df_match[df_match['ins'] == ins]['total'].cumsum(),
                     index=df_match.index
                            )
        temps.rename(columns= {'total': 'cur_total'}, inplace=True)
        df_match = df_match.merge(temps, left_index=True, right_index=True)
    df_match[['cur_total_x', 'cur_total_y']] = df_match[['cur_total_x',  'cur_total_y']].fillna(0)
    return df_match['cur_total_x'] + df_match['cur_total_y']

def process_match(match_id, diction):
    new_df = pd.DataFrame()
    for idx, ins in enumerate(['1st innings', '2nd innings']):
        if (len(diction['innings']) == 1) & (ins == '2nd innings'):
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

def get_dl_par(df: pd.DataFrame, df_dls: pd.DataFrame) -> pd.DataFrame:
    """Caclulates the DLS par score for each match in df

    Args:
        df (pd.DataFrame): df containing ball by ball data
        df_dls (pd.DataFrame): DLS dataframe

    Returns:
        pd.DataFrame: new dataframe with caclulated par score
    """
    all_matches = pd.DataFrame()
    for matches in tqdm(df['match_id'].unique()):
        try:
            df_match = df[df['match_id'] == matches].copy()
            df_match = df_match.reset_index()
            df_match['cur_total'] = get_current_runs(df_match)
            df_match['ball_dead'] = df_match['extras_type'].apply(is_dead_ball)
            in_1_total = df_match[df_match['ins'] == '1st innings']['cur_total'].max()
            df_2nd = df_match[df_match['ins'] == '2nd innings']
            for idx, balls in df_2nd.iterrows():
                wickets_left = 10 - df_2nd.loc[:idx]['player_out'].count()
                if wickets_left == 0:
                    all_matches = pd.concat([all_matches, df_match])
                    break
                # cur_runs = df_2nd.loc[idx]['cur_total']
                balls_bowled = balls['index'] - df_2nd.loc[:idx]['ball_dead'].sum()
                res_2nd_team = df_dls.loc[balls_bowled + 1, str(wickets_left)]
                dl_par = in_1_total * (100 - res_2nd_team) / 100
                df_match.loc[idx, 'dl_par'] = dl_par
        except Exception as e:
            print(e)
        all_matches = pd.concat([all_matches, df_match])
    all_matches['dls_winner'] = all_matches.apply(lambda x: dls_winner(x), axis=1)
    all_matches['dls_correct'] = all_matches['dls_winner'] == all_matches['winner']
    all_matches['over_pre'] = all_matches['over'].apply(str).str.split('.').apply(lambda x: int(x[0]))
    all_matches = all_matches.dropna(subset=['dl_par'])
    return all_matches

def dls_winner(row):
    teams = [row['team_1'], row['team_2']]
    bat_1st = row['team_bat_first']
    if row['cur_total'] < row['dl_par']:
        dls_winner = bat_1st
    else:
        teams.remove(bat_1st)
        dls_winner = teams[0]
    return dls_winner


def handle_datestr(str_i):
    str_in = str_i
    non_numeric_chars = string.printable[10:]
    table = str.maketrans(dict.fromkeys(non_numeric_chars))
    str_in = str_in.translate(table)
    if len(str_in) == 7:
        str_in = str_in[:4] + '0' + str_in[4:]
    if len(str_in) == 6:
        str_in = str_in[:4] + '0' + str_in[4] + '0' + str_in[5]
    try:
        return pd.to_datetime(str_in)
    except Exception as e:
        return np.nan

def filter_interrupted_matches(df):
    df['bowl_again'] = df['extras_type'].isin(['wides', 'noballs'])
    df = df[df['ins'] == '1st innings']
    count = df.groupby(['match_id']).count()
    summed = df.groupby(['match_id']).sum()
    wickets = count['kind']
    balls_bowled = count['bowl_again'] - summed['bowl_again']
    wickets = wickets[(balls_bowled == 300) | (wickets == 10)]
    return wickets.index


