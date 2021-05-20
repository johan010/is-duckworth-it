import pandas as pd
from src.data.process_data import fetch_all_matches, load_dls
from src.utils.utils import get_dl_par, dls_winner, handle_datestr
from src.visualization.visuals import plot_dls, get_meta_info

import seaborn as sns
import matplotlib.pyplot as plt

def plot_male_odi_dls_acc():
    df = fetch_all_matches()
    df = df[df['match_id'].isin(filter_interrupted_matches(df))]
    df_dls = load_dls()
    df2 = get_dl_par(df, df_dls)
    df_male = df2[df2['gender'] == 'male']
    grouped_male = df_male.groupby('over_pre').sum() / df_male.groupby('over_pre').count() * 100
    plot_dls(grouped_male, 'male_odi')
    get_meta_info(df_male)



df = fetch_all_matches()
df = df[df['match_id'].isin(filter_interrupted_matches(df))]
df_dls = load_dls()
df2 = get_dl_par(df, df_dls)
df_male = df2[df2['gender'] == 'male']
df_male['dates'] = df_male['dates'].apply(handle_datestr)

year_group_sum = df_male.groupby(['dates', 'over_pre']).sum()['dls_correct']
year_group_count = df_male.groupby(['dates', 'over_pre']).count()['dls_correct']

by_year_sum = year_group_sum.groupby([pd.Grouper(freq='1y', level='dates'),
                        pd.Grouper(level='over_pre'),]
                        ).sum().reset_index()

by_year_count= year_group_count.groupby([pd.Grouper(freq='1y', level='dates'),
                        pd.Grouper(level='over_pre'),]
                        ).sum().reset_index()                        
by_year_sum['dls_correct'] = by_year_sum['dls_correct'] / by_year_count['dls_correct'] * 100
by_year_sum['dates'] = by_year_sum['dates'].dt.strftime('%Y')
id = 'Dry_Run 2_76'
id.replace(' ', '-')

sns.set(rc={'figure.figsize':(15,10)})
sns.lineplot(x='over_pre',
             y='dls_correct',
             data=by_year_sum,
             hue='dates',
             palette='viridis')
plt.xlabel('Overs Bowled')
plt.ylabel('Prediction Accuracy (%)')
plt.savefig('dls_acc_by_year.png')


sns.set(rc={'figure.figsize':(15,10)})

sns.lineplot(x='dates',
             y='dls_correct',
             data=by_year_sum,
             ci='sd',
             err_style='band')
sns.despine()
plt.xlabel('Year')
plt.ylabel('Average Prediction Accuracy (%)')
plt.title('Average DLS accuracy by year')
plt.ylim(0, 100)
plt.savefig('avg_acc_by_year.png')

countries = ['Afghanistan', 'Australia', 'Bangladesh', 'England', 'India', 'Ireland', 
 'New Zealand', 'Pakistan', 'South Africa', 'Sri Lanka', 'West Indies', 'Zimbabwe']
df_male = df_male[(df_male['team_1'].isin(countries)) & (df_male['team_2'].isin(countries))]
country_sum = df_male.groupby(['team_2', 'over_pre']).sum()['dls_correct'].reset_index()
country_count = df_male.groupby(['team_2', 'over_pre']).count()['dls_correct'].reset_index()
country_sum['dls_correct'] = country_sum['dls_correct'] / country_count['dls_correct'] * 100
sns.set(rc={'figure.figsize':(15,10)})
sns.barplot(x='team_2',
             y='dls_correct',
             data=country_sum)
sns.despine()
plt.xticks(rotation=90)
plt.xlabel('Country')
plt.ylabel('Average Prediction Accuracy (%)')
plt.title('Average DLS accuracy by country')
plt.ylim(0, 100)
plt.savefig('avg_acc_by_country.png')