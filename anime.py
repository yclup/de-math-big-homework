#这个程序从萌娘百科(https://zh.moegirl.org)爬取最原始的数据
import requests
from bs4 import BeautifulSoup
import re
import json
MAIN = r"https://zh.moegirl.org/%E5%8A%A8%E7%94%BB"
MAIN_ROUTE = r"https://zh.moegirl.org"
SAVE_FILE = 'data.txt'


def get_HTML(url: str):
    try:
        kv = {'user-agent': 'Mozilla/5.0'}
        r = requests.get(url, timeout=30, headers=kv)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r
    except:
        return None


class Anime:

    def __init__(self, name, cast_list, year):
        self.name = name
        self.cast_list = cast_list
        self.year = year


class AnimeByYear:

    def __init__(self, href):
        self.info = href.text
        self.href = href.attrs['href']
        self.year = self.get_year(self.info)
        self.route = MAIN_ROUTE + self.href
        self.anime_list = []

    def get_year(self, string):
        return ''.join(filter(str.isdigit, string))

    def get_year_page(self):
        self.year_page = get_HTML(self.route)
        soup = BeautifulSoup(self.year_page.text, 'html.parser')
        self.casts = soup.find_all(
            'span', {'class': "mw-headline", 'id': re.compile("^CAST")})
        self.cast_list = []
        for item in self.casts:
            try:
                if item.parent.findNextSibling().name == 'table':
                    title = item.parent.findPreviousSibling('h2').text
                    cast_list = [tr.text for tr in item.parent.findNext(
                        'tbody').findChildren('tr')]
                    self.anime_list.append(Anime(title, cast_list, self.year))
                elif item.parent.findNextSibling().name in ['ul', 'div']:
                    title = item.parent.findPreviousSibling('h2').text
                    cast_list = [cld.text for cld in item.parent.findNext(
                        'ul').findChildren()]
                    self.anime_list.append(Anime(title, cast_list, self.year))
                else:
                    continue
            except:
                continue
        print(self.info, 'OK')


def get_main_links():
    main_page = get_HTML(MAIN)
    soup = BeautifulSoup(main_page.text, 'html.parser')
    hrefs = soup.find_all('a', {'title': re.compile('^日本.+动画$')})
    return hrefs


def save_data(year_list, save_file):
    database = []
    for year in year_list:
        anime_list = year.anime_list
        for anime in anime_list:
            info = {'year': anime.year, 'name': anime.name,
                    'cast': anime.cast_list}
            database.append(info)
        print(year.year, 'OK')
    with open(save_file, encoding='utf-8', mode='w') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

def main():
    links = get_main_links()
    year_list = []
    for link in links:
        a = AnimeByYear(link)
        a.get_year_page()
        year_list.append(a)
    save_data(year_list, SAVE_FILE)


main()