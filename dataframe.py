import pandas as pd
import re
import numpy as np
import os

pd.set_option('display.max_columns', None)


def get_means(match_name, team_name):
    base_filename = r'C:\Users\erwin\Dropbox\PythonScripts\aussierulestipping\Matches\2018\\'

    init_df = pd.read_csv(base_filename + match_name)
    init_df.replace(u'\xa0', np.nan, regex=True, inplace=True)

    init_df['Age_year'] = init_df.loc[:, 'Age'].apply(lambda x: re.search('\w*(?=y)',
                                                                          x).group(0)).astype(float)
    init_df['Career_game_%'] = init_df.loc[:, 'Career Games (W-D-L W%)'].apply(lambda x: re.search('\w*.\w*(?=%)',
                                                                                                   x).group(0)).astype(
        float)
    init_df['Career_game_total'] = init_df.loc[:, 'Career Games (W-D-L W%)'].apply(lambda x: re.search('\w*.\w*(?=\()',
                                                                                                       x).group(
        0)).astype(float)
    init_df['Career_goals_total'] = (init_df.loc[init_df['Career Goals (Ave.)'].isnull() != True, 'Career Goals (Ave.)']
                                     .apply(lambda x: re.search('\w*.(?=\()', x).group(0))
                                     .astype(float))
    init_df['Career_goals_avg'] = (init_df.loc[init_df['Career Goals (Ave.)'].isnull() != True, 'Career Goals (Ave.)']
                                   .apply(lambda x: re.search('\w*.\w*(?=\))', x).group(0))
                                   .astype(float))
    # print(team_name)
    if team_name == 'Greater Western Sydney':
        team_name = 'GWS'

    init_df.drop(
        labels=['Unnamed: 0', '#_x', 'Player', 'Age', team_name + ' Games (W-D-L W%)', team_name + ' Goals (Ave.)',
                'Career Games (W-D-L W%)', 'Career Goals (Ave.)'], axis=1, inplace=True)
    init_df = init_df[:].astype(float)

    means = init_df.mean()
    return means


def create_dataframe(team_name):
    # Need to add round/team information in this dataframe
    filenames = os.listdir(path=r'C:\Users\erwin\Dropbox\PythonScripts\aussierulestipping\Matches\2018')
    game_list = []
    for file in filenames:
        if '- ' + str(team_name) + '.csv' in file:
            game_list.append(file)

    def get_second_team(team_name, string):
        if 'Final' in string:
            first_team = re.search('(?<=Final ).*(?= vs)', string).group(0)
        else:
            first_team = re.search('(?<=\d ).*(?= vs)', string).group(0)

        second_team = re.search('(?<=vs ).*(?= -)', string).group(0)

        if team_name == first_team:
            return second_team
        else:
            return first_team

    def get_series(game_title, team_name):
        means = get_means(game_title, team_name)
        afl_round = re.search('(?<=Round )\d\d|\d|([A-Z])\w+\s([A-Z])\w+', game_list[0]).group(0)
        team_1 = team_name
        team_2 = get_second_team(team_name, game_title)
        list_before_series = [afl_round, team_1, team_2]
        starting_round = pd.Series(list_before_series, index=['Round', 'Team 1', 'Team 2'])
        series = means.append(starting_round)
        return series

    final_df = pd.DataFrame(get_series(game_list[0], team_name)).transpose()

    for game in game_list[1:]:
        final_df = final_df.append(get_series(game, team_name), ignore_index=True)

    return final_df


# essendon_df = create_dataframe('West Coast')
# print(essendon_df)


afl_teams_list = ['Richmond', 'Carlton', 'Essendon', 'Adelaide', 'St Kilda', 'Brisbane Lions', 'Port Adelaide',
                  'Fremantle', 'Gold Coast', 'North Melbourne', 'Hawthorn', 'Collingwood', 'Greater Western Sydney',
                  'Western Bulldogs', 'Melbourne', 'Geelong', 'West Coast', 'Sydney']


def create_year_stats_dataframe(afl_teams_list):
    base_df = create_dataframe(afl_teams_list[0])
    for team in afl_teams_list[1:]:
        base_df = pd.concat([base_df, create_dataframe(team)], axis=0)
    return base_df


df_2018 = create_year_stats_dataframe(afl_teams_list)
print(df_2018)

