import pandas as pd
import re
import numpy as np
import os

filenames = os.listdir(path=r'C:\Users\erwin\Dropbox\PythonScripts\aussierulestipping\Matches\2018')


def get_means(match_name):
    base_filename = r'C:\Users\erwin\Dropbox\PythonScripts\aussierulestipping\Matches\2018\\'

    init_df = pd.read_csv(base_filename+match_name)
    init_df.replace(u'\xa0', np.nan, regex=True, inplace=True)

    init_df['Age_year'] = init_df.loc[:, 'Age'].apply(lambda x: re.search('\w*(?=y)',
                                                                   x).group(0)).astype(float)
    init_df['Career_game_%'] = init_df.loc[:, 'Career Games (W-D-L W%)'].apply(lambda x: re.search('\w*.\w*(?=%)',
                                                                   x).group(0)).astype(float)
    init_df['Career_game_total'] = init_df.loc[:, 'Career Games (W-D-L W%)'].apply(lambda x: re.search('\w*.\w*(?=\()',
                                                                   x).group(0)).astype(float)
    init_df['Career_goals_total'] = (init_df.loc[init_df['Career Goals (Ave.)'].isnull() != True, 'Career Goals (Ave.)']
                                     .apply(lambda x: re.search('\w*.(?=\()', x).group(0))
                                     .astype(float))
    init_df['Career_goals_avg'] = (init_df.loc[init_df['Career Goals (Ave.)'].isnull() != True, 'Career Goals (Ave.)']
                                     .apply(lambda x: re.search('\w*.\w*(?=\))', x).group(0))
                                     .astype(float))

    init_df.drop(labels = ['Unnamed: 0', '#_x', 'Player', 'Age', 'Essendon Games (W-D-L W%)', 'Essendon Goals (Ave.)',
                           'Career Games (W-D-L W%)', 'Career Goals (Ave.)'], axis=1, inplace=True)
    init_df = init_df[:].astype(float)

    means = init_df.mean()
    return means


def create_dataframe(team_name):
    game_list = []
    for file in filenames:
        if str(team_name)+'.csv' in file:
            game_list.append(file)
    # print(len(game_list))
    means = get_means(game_list[0])
    mean_df = pd.DataFrame(means).transpose()
    # print(mean_df.head())

    starting_means = get_means(game_list[1])
    final_df = mean_df.append(starting_means, ignore_index=True)

    for game in game_list[2:]:
        game_means = get_means(game)
        # print(game_means)
        final_df = final_df.append(game_means, ignore_index=True)

    print(final_df)


create_dataframe('Essendon')

