import bs4
from bs4 import NavigableString
import requests
import re
import pandas as pd

pd.set_option('display.max_columns', None)


class BsScrapeYear:

    def __init__(self, url):
        self.url = url
        self.year =re.search('\d\d\d\d', url).group(0)
        self.res = requests.get(self.url)
        self.year_soup = bs4.BeautifulSoup(self.res.text, "lxml")
        self.final_links = self.year_soup.select('b + a[href]')
        # Gets the url for the individual games
        # Have a missing game but don't know where it is.
        # Not the complete urls for each game.
        self.game_urls = []
        for link in self.final_links:
            game_url = link.get('href')
            if 'game' in game_url:
                # The urls in self.game_urls have the format '../stats/games/2018/031420180322.html'
                # Have to remove the leading two dots.
                self.game_urls.append('https://afltables.com/afl' + game_url[2:])

    def get_game_urls(self):
        return self.game_urls

    def get_round_ladders(self):
        round_dict = {}
        for i in range(1, 24):
            text_to_search = 'Rd ' + str(i) + ' Ladder'
            round_table = self.year_soup.find(text=text_to_search).find_parent('table')
            round_table_list = []
            for afl_round in round_table:
                if isinstance(afl_round, NavigableString):
                    continue
                else:
                    round_table_list.append([r.text for r in afl_round])
            round_dict[str(i)] = round_table_list
        # Returns a dictionary with keys being the round number and values being the complete round ladder table.
        return round_dict

    def csv_summaries(self):
        game_summaries = []
        for url in self.game_urls:
            game = BsScrapeGame(url)
            summary = game.get_summary()
            # Throws away any games with extra time (Haven't figured out a way to deal with them yet)
            ########## COME BACK TO ME.
            if len(summary) < 21:
                game_summaries.append(summary)

        summary_headings = ['Round/Venue/Date/Time/Attendance', 'Team1', 'T1_Q1_Points', 'T1_Q2_Points', 'T1_Q3_Points',
                            'T1_Q4_Points', 'Team2', 'T2_Q1_Points', 'T2_Q2_Points', 'T2_Q3_Points', 'T2_Q4_Points',
                            'Q1_Margin',
                            'Q2_Margin', 'Q3_Margin', 'Q4_Margin', 'Q1_Scores', 'Q2_Scores', 'Q3_Scores', 'Q4_Scores',
                            'Umpires']

        summaries_df = pd.DataFrame.from_records(game_summaries, columns=summary_headings)
        # Creates the csv file for the game summaries from the pd dataframe.
        filepath = r'C:\Users\erwin\Dropbox\PythonScripts\aussierulestipping\Summaries\%s.csv' % self.year
        # print(filepath)
        summaries_df.to_csv(path_or_buf=filepath, index=True)


class BsScrapeGame:

    def __init__(self, game_url):
        self.url = game_url
        self.res = requests.get(self.url)
        # Definitely get different(better) results from using the lxml parser.
        self.match_data = bs4.BeautifulSoup(self.res.text, "lxml")
        # print(self.match_data)
        # Selects every <a> element with a href attribute starting with '../../../teams'.
        self.team1 = self.match_data.select('a[href^="../../../teams"]')[0].text
        self.team2 = self.match_data.select('a[href^="../../../teams"]')[1].text
        self.round = ''
        self.team1_stats_dict = ''
        self.team2_stats_dict = ''
        self.team1_player_details_dict = ''
        self.team2_player_details_dict = ''
        self.score_progression = ''

    def get_summary(self):
        top_table = self.match_data.find_all('table')[0]
        table_info = top_table.find_all('td')
        score_list = []
        for r in table_info:
            score_list.append(r.text)
        # Removes the back and forth arrows.
        score_list.pop(0)
        score_list.pop(1)
        # Removes the label Qrt margin
        score_list.pop(11)
        # Removes the label Qrt scores
        score_list.pop(15)
        # Removes the label Umpires
        score_list.pop(19)
        # print(score_list[0])
        self.round = re.search('(?<=Round: )\d\d|\d|([A-Z])\w+\s([A-Z])\w+', score_list[0]).group(0)
        # Returns a simple list with the game summary
        return score_list

    def get_player_stats(self):
        # summary_tables has a length of 4 for the 4 different tables on the page.
        # Returns the conjoined thead and tbody data for each table.
        summary_tables = self.match_data.select('.sortable')
        team1_stats = summary_tables[0]
        team2_stats = summary_tables[1]
        team1_player_details = summary_tables[2]
        team2_player_details = summary_tables[3]

        # team_stats has a length of 22 for all of the players on the team.

        def process_team_stats(table_name):
            # table_name.find_all('tbody') returns a bs4 results set. (Formatted as a list)
            # If you want to further use css selectors on the results set, you have to take the first item of the list.
            header = table_name.find_all('thead')[0].find_all('tr')
            team_stats = table_name.find_all('tbody')[0]

            def get_header_info(header_info):
                info_list = []
                for info in header_info:
                    info_list.append(info.text)
                return info_list

            top_header = get_header_info(header[0])
            bot_header = get_header_info(header[1])

            # base_dict = {}
            base_list = []
            base_list.append(top_header)
            base_list.append(bot_header)

            # base_dict['Top Header'] = top_header
            # base_dict['Bottom Header'] = bot_header

            for player in team_stats:
                individual_info = player.find_all('td')
                player_stats = []
                for stat in individual_info:
                    player_stats.append(stat.text)
                base_list.append(player_stats)
            return base_list

        self.team1_stats_dict = process_team_stats(team1_stats)
        self.team2_stats_dict = process_team_stats(team2_stats)
        self.team1_player_details_dict = process_team_stats(team1_player_details)
        self.team2_player_details_dict = process_team_stats(team2_player_details)
        # Returns dictionaries with keys being the top/bottom headers and player names.
        return self.team1_stats_dict, self.team2_stats_dict, self.team1_player_details_dict, self.team2_player_details_dict

    def csv_player_stats(self):

        def create_team_csv(team_stats, player_details, team_index):
            team_names = [self.team1, self.team2]
            team_stats_df = pd.DataFrame.from_records((team_stats[2:]), columns=team_stats[1])
            team_player_details_df = pd.DataFrame.from_records((player_details[2:]), columns=player_details[1])
            combined_df = pd.merge(team_stats_df, team_player_details_df, on='Player')
            combined_df.drop('#_y', axis=1, inplace=True)
            # Creates the csv file for the game summaries from the pd dataframe.
            filepath = r'C:\Users\erwin\Dropbox\PythonScripts\aussierulestipping\Matches\2018\Round %s %s vs %s - ' \
                       r'%s.csv' % (self.round, self.team1, self.team2, team_names[team_index])
            combined_df.to_csv(path_or_buf=filepath, index=True)

        create_team_csv(self.team1_stats_dict, self.team1_player_details_dict, 0)
        create_team_csv(self.team2_stats_dict, self.team2_player_details_dict, 1)

    def csv_score_progression(self):
        copy_progression = self.score_progression.copy()
        for index, item in enumerate(copy_progression):
            if type(item) != list:
                copy_progression.pop(index)
        scoring_progression_df = pd.DataFrame.from_records(copy_progression[1:], columns=copy_progression[0])
        filepath = r'C:\Users\erwin\Dropbox\PythonScripts\aussierulestipping\Matches\2018\Round %s %s vs %s - ' \
                   r'Scoring Progression.csv' % (self.round, self.team1, self.team2)
        scoring_progression_df.to_csv(path_or_buf=filepath, index=True)

    def get_scoring_progression(self):
        top_body = self.match_data.find_all('table')
        scoring_progression_table = top_body[len(top_body) - 1]
        scoring_progression_stats = scoring_progression_table.find_all('tr')
        scoring_progression_output = []
        for progress in scoring_progression_stats:
            if len(progress) != 1:
                # th element tag is only used for the column headings (Team name, Time, Score, Other team Time,
                # Other team name)
                th = [x.text for x in progress.find_all('th')]
                td = [x.text for x in progress.find_all('td')]
                y = []
                if th != y:
                    scoring_progression_output.append(th)
                if td != y:
                    scoring_progression_output.append(td)
            elif len(progress) == 1:
                if progress.find('td') is not None:
                    x = progress.find('td')
                    y = x.find('b')
                    findings = re.search('(([1-4][a-z][a-z]|Final) quarter \(\d*m \d*s\))|'
                                         '([1-9][a-z][a-z] Extra Time \(\d*m \d*s\))', y.text).group(0)
                    scoring_progression_output.append(findings)
        # Returns a simple list of lists with individual rows having their own lists.
        self.score_progression = scoring_progression_output
        return scoring_progression_output


year_url_2018 = 'https://afltables.com/afl/seas/2018.html'
game_url2018 = 'https://afltables.com/afl/stats/games/2018/031420180322.html'
game_url2017 = 'https://afltables.com/afl/stats/games/2017/131820170909.html'


# # Testing year scraping
# twentyeighteen = BsScrapeYear(year_url_2018)
# # print(twentyeighteen.get_round_ladders())
# urls_2018 = twentyeighteen.get_game_urls()
# twentyeighteen.csv_summaries()

# Testing game scraping
# def test_game_scrape_functions(game_url):
#     game = BsScrapeGame(game_url)
#
#     # summary = game.get_summary()
#     # print(summary)
#     #
#     # a, b, c, d = game.get_player_stats()
#     # print(a)
#     # print(b)
#     # print(c)
#     # print(d)
#     #
#     # print(game.get_scoring_progression())
#     # print(game.round)
#     game.get_summary()
#     # print('Game round is: ', game.round)
#     game.get_player_stats()
#     game.get_scoring_progression()
#     game.csv_player_stats()
#     game.csv_score_progression()
#
#
# test_game_scrape_functions(game_url2018)

# # Testing game scraping for the year.
# twentyeighteen = BsScrapeYear(year_url_2018)
# urls_2018 = twentyeighteen.get_game_urls()
# for url in urls_2018:
#     test_game_scrape_functions(url)
