import bs4
import requests
import re


url = 'https://afltables.com/afl/seas/2018.html'
game_url1 = 'https://afltables.com/afl/stats/games/2018/031420180322.html'


class BsScrapeYear:

    def __init__(self, url):
        self.url = url
        self.res = requests.get(self.url)
        self.year_data = bs4.BeautifulSoup(self.res.text, "html.parser")
        self.final_links = self.year_data.select('b + a[href]')
        # Gets the url for the individual games
        # Have a missing game but don't know where it is.
        self.game_urls = []
        for link in self.final_links:
            game_url = link.get('href')
            if 'game' in game_url:
                self.game_urls.append(game_url)

    def get_game_urls(self):
        base_afltables_url = 'https://afltables.com/afl'
        # The urls in self.game_urls have the format '../stats/games/2018/031420180322.html'
        # Have to remove the leading two dots.
        complete_urls = [base_afltables_url + game_url[2:] for game_url in self.game_urls]
        # Return a list of the complete game urls for the season.
        return complete_urls


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

        return team1_stats_dict, team2_stats_dict, team1_player_details_dict, team2_player_details_dict

    def get_scoring_progression(self):
        top_body = self.match_data.find_all('table')
        scoring_progression_table = top_body[len(top_body)-1]
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
                    findings = re.search('([1-4][a-z][a-z]|Final) quarter \(\d\dm \d*s\)', y.text).group(0)
                    scoring_progression_output.append(findings)
        return scoring_progression_output


twentyeighteen = BsScrapeYear(url)

game_one = BsScrapeGame(game_url1)

scores = game_one.get_scores()
print(scores)

a, b, c, d = game_one.get_player_stats()
print(a)
print(b)
print(c)
print(d)

print(game_one.get_scoring_progression())




