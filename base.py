import bs4
import requests
import re
# from selenium import webdriver


url = 'https://afltables.com/afl/seas/2018.html'
game_url1 = 'https://afltables.com/afl/stats/games/2018/031420180322.html'

# driver = webdriver.Firefox()
# driver.get(game_url1)
#
# html = driver.page_source
# soup = bs4.BeautifulSoup(html, "html.parser")
#
# print(soup)



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
        return complete_urls


class BsScrapeGame:

    def __init__(self, game_url):
        self.url = game_url
        self.res = requests.get(self.url)
        self.match_data = bs4.BeautifulSoup(self.res.text, "html.parser")
        # Selects every <a> element with a href attribute starting with '../../../teams'.
        self.team1 = self.match_data.select('a[href^="../../../teams"]')[0].text
        self.team2 = self.match_data.select('a[href^="../../../teams"]')[1].text

    def get_scores(self):
        top_table = self.match_data.find_all('table')[0]
        table_info = top_table.find_all('td')
        for r in table_info:
            print(r.text)
        return top_table

    def get_player_stats(self):
        # top_body has a length of 4 for the 4 different tables on the page.
        top_body = self.match_data.find_all('tbody')[3]
        # player_info has a length of 22 for all of the players on the team.
        player_info = top_body.find_all('tr')[21]
        player_stats = player_info.find_all('td')
        print('Length of player_info: ', len(player_info))
        for stat in player_stats:
            if stat.text == '':
                print('NaN')
            else:
                print(stat.text)
        # print(player_info[0])
        # for body in player_info:
        #     print(body)

    def get_scoring_progression(self):
        top_body = self.match_data.find_all('table')
        print(len(top_body))
        scoring_progression_table = top_body[len(top_body)-1]
        scoring_progression_stats = scoring_progression_table.find_all('tr')
        print('scoring_progression length: ', len(scoring_progression_stats))
        # print(scoring_progression_stats)
        for progress in scoring_progression_stats:
            if progress.text == '':
                print('Nothing')
            elif len(progress) != 1:
                # print(len(progress))
                th = [x.text for x in progress.find_all('th')]
                td = [x.text for x in progress.find_all('td')]
                y = []
                if th != y:
                    print(th)
                if td != y:
                    print(td)
            elif len(progress) == 1:
                if progress.find('td') is not None:
                    x = progress.find('td')
                    # print(len(x))
                    y = x.find('b')
                    print(re.search('([1-4][a-z][a-z]|Final) quarter \(\d\dm \d*s\)', y.text).group(0))






# class BsScrapeRound:
#     def __init__(self, round):
#         self.round = round
#         self.res = requests.get(self.url)
#         self.round_data = self.year_data.select('div h1')

twentyeighteen = BsScrapeYear(url)
# print(twentyeighteen.get_game_urls())

game_one = BsScrapeGame(game_url1)
print(game_one.team1, game_one.team2)
# scores = game_one.get_scores()
# game_one.get_player_stats()
game_one.get_scoring_progression()

# print(twentyeighteen.round_data[0])
#
# print(twentyeighteen.round_data[1])

# print(twentyeighteen.round_data[4].text)
# print(len(twentyeighteen.round_data))

# for i in range(0):
#     print(twentyeighteen.links[i])
# print(twentyeighteen.links)

# # print(twentyeighteen.html)
# print(len(twentyeighteen.html))
#
#
# print(twentyeighteen.final_links)
# print(len(twentyeighteen.final_html))
# print(twentyeighteen.final_html)
# for i in range(10):
#     print(twentyeighteen.round_data[i].text)

# body > center > table:nth-child(50) > tbody > tr