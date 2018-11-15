import bs4
import requests


url = 'https://afltables.com/afl/seas/2018.html'


class BsScrapeYear:

    def __init__(self, url):
        self.url = url
        self.res = requests.get(self.url)
        self.year_data = bs4.BeautifulSoup(self.res.text, "html.parser")
        self.round_data = self.year_data.select('tr td')
        self.final_links = self.year_data.select('b + a[href]')
        # Gets the url for the individual games/venues.
        # Have to clean up so it only contains the games.
        # Have a missing game but don't know where it is.
        self.game_urls = [link.get('href') for link in self.final_links]

# class BsScrapeRound:
#     def __init__(self, round):
#         self.round = round
#         self.res = requests.get(self.url)
#         self.round_data = self.year_data.select('div h1')

twentyeighteen = BsScrapeYear(url)
# print(twentyeighteen.round_data[0])
#
# print(twentyeighteen.round_data[1])

# print(twentyeighteen.round_data[4].text)
# print(len(twentyeighteen.round_data))

# for i in range(0):
#     print(twentyeighteen.links[i])
# print(twentyeighteen.links)

# print(twentyeighteen.html)
print(len(twentyeighteen.html))


print(twentyeighteen.final_links)
print(len(twentyeighteen.final_html))
print(twentyeighteen.final_html)
# for i in range(10):
#     print(twentyeighteen.round_data[i].text)

# body > center > table:nth-child(50) > tbody > tr