import bs4
from bs4 import NavigableString
import requests
import re
import pandas as pd

url_year = 'https://afltables.com/afl/seas/2017.html'
game_url2018 = 'https://afltables.com/afl/stats/games/2018/031420180322.html'
game_url2017 = 'https://afltables.com/afl/stats/games/2017/131820170909.html'


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

    def get_summaries(self):
        game_summaries = []
        for url in self.game_urls:
            game = BsScrapeGame(url)
            summary = game.get_scores()
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
        print(filepath)
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

    def get_scores(self):
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

            base_dict = {}

            base_dict['Top Header'] = top_header
            base_dict['Bottom Header'] = bot_header

            for player in team_stats:
                individual_info = player.find_all('td')
                player_stats = []
                for stat in individual_info:
                    player_stats.append(stat.text)
                base_dict[player_stats[1]] = player_stats
            return base_dict

        team1_stats_dict = process_team_stats(team1_stats)
        team2_stats_dict = process_team_stats(team2_stats)
        team1_player_details_dict = process_team_stats(team1_player_details)
        team2_player_details_dict = process_team_stats(team2_player_details)
        # Returns dictionaries with keys being the top/bottom headers and player names.
        return team1_stats_dict, team2_stats_dict, team1_player_details_dict, team2_player_details_dict

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
        return scoring_progression_output


################### Testing year scraping
twentyeighteen = BsScrapeYear(url_year)
# print(twentyeighteen.get_round_ladders())
urls_2018 = twentyeighteen.get_game_urls()
twentyeighteen.get_summaries()

# ################### Testing game scraping
# def test_game_scrape_functions(game_url):
#     game_one = BsScrapeGame(game_url)
#
#     scores = game_one.get_scores()
#     print(scores)
#
#     a, b, c, d = game_one.get_player_stats()
#     print(a)
#     print(b)
#     print(c)
#     print(d)
#
#     print(game_one.get_scoring_progression())
#
# # test_game_scrape_functions(game_url2017)
#
# ################### Testing game scraping for the year.
# for url in urls_2018:
#     test_game_scrape_functions(url)
