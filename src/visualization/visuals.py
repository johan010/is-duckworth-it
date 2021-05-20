import matplotlib.pyplot as plt
import pandas as pd


def plot_dls(df_grouped, filename):
    plt.Figure(figsize=(15,10))
    plt.plot(df_grouped['dls_correct'])
    # plt.plot(grouped_female['dls_correct'])
    plt.title('Accuracy of Duckworth Lewis Stern at different points in a game (male ODIs)')
    plt.xlabel('Overs Bowled')
    plt.ylabel('Prediction Accuracy (%)')
    plt.savefig(filename)
    plt.close()

def get_meta_info(df: pd.DataFrame):
    print('number of matches processed: ' + str(df['match_id'].nunique()))