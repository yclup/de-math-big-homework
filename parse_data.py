# 这个程序负责分析数据、导出数据、整理数据等工作

# for year in year_list:
#         anime_list = year.anime_list
#         for anime in anime_list:
#             info = {'year': anime.year, 'name': anime.name,
#                     'cast': anime.cast_list}
#             database.append(info)

import json
import networkx
from itertools import combinations
from matplotlib import pyplot as plt
import requests
from bs4 import BeautifulSoup
import os
import re
from selenium import webdriver
import time
from math import log, sqrt

SAVE_FILE = 'data.txt'  # 原始数据保存在SAVE_FILE中
NEW_SAVE_FILE = 'vadata.txt'  # 该文件没有用
EDGE_INFO = 'edge_info.txt'  # 以json格式保存边的信息
POS_INFO = 'pos_info.txt'  # 保存节点的位置信息
INTRODUCTION_ROUTE = "introduction"  # 保存声优的图片及介绍的文件夹
GRAPH_PATH = "graph.gpickle"  # 保存networkx生成的图
CENTRALITY_INTO = "centrality_info.txt"  # 保存节点中心度信息，暂时没有用


def get_results_number(wd, driver):  # 以下三个函数用来获得动漫在百度中的搜索结果条数以反映其重要程度
    try:
        inputbox = driver.find_element_by_id("kw")
        inputbox.clear()
        inputbox.send_keys(wd)
        search = driver.find_element_by_id("su")
        search.click()
        time.sleep(1)
        num_text = driver.find_element_by_class_name("nums_text")
    except Exception as e:
        print(e)
        print("anime_name" + wd + "failed")
        return
    num = extract_number(num_text.text)
    return num


def extract_number(nums_text):
    pattern = re.compile("\\d+")
    nums_text = nums_text.replace(',', '')
    return re.findall(pattern, nums_text)[0]


def add_results_number():
    database = get_data(SAVE_FILE)
    driver = webdriver.Firefox()
    driver.get(r"https://www.baidu.com/s?wd=%E7%99%BE%E5%BA%A6")
    for anime in database:
        try:
            anime['score'] = get_results_number(anime['name'], driver)
            print("{}, OK, score: {}".format(anime['name'], anime['score']))
        except Exception as e:
            print(e)
    with open(SAVE_FILE, encoding='utf-8', mode='w') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)


def isnotenter(string):
    return string != "\n"


def format_info(string):  # 用来剔除无用的数据，保证数据的准确性
    string = string.strip()
    parts = string.split()
    if len(parts) != 1:
        return None
    if '：' not in string:
        return None
    if '[' in string:
        pos = string.find('[')
        string = string[:pos]
    if 'CV' in string:
        return None
    if '、' in string:
        return None
    string = ''.join(filter(isnotenter, string))
    pack = string.split('：')
    if len(pack) != 2:
        return None
    else:
        charactor, va = pack
        cv_route = "{}/{}".format(INTRODUCTION_ROUTE, va)
        if not os.path.exists(cv_route):
            return None
    if va in ['秋本ねりね', '青叶苹果', 'うらたぬき', '森七菜', '醍醐虎汰朗', '浜边美波', 'アニプレックス', '杏子御津', '民安ともえ']:
        return None
    return charactor, va


def get_data(save_file):  # 用来从文件中读取数据
    with open(save_file, encoding='utf-8') as f:
        database = json.load(f)
        return database


class VoiceActor:

    def __init__(self, name):
        self.name = name
        self.betweenness_centrality = 0
        self.closeness_centrality = 0

    def __repr__(self):
        return self.name


def get_weight(anime, cv1, cv2):
    score_factor = float(anime["score"])
    index_factor = float(anime['cast'].index(
        cv1) + anime['cast'].index(cv2)) / len(anime['cast'])
    return (sqrt(index_factor) / log(score_factor, 10)) * 50


def to_json(database):
    edge_dic = []
    for anime in database:
        year = anime['year']
        name = anime['name']
        for a, b in combinations(anime['cast'], 2):
            try:
                a_char, a_cv = format_info(a)
                b_char, b_cv = format_info(b)
                weight = get_weight(anime, a, b)
                edge_dic.append({
                    'start_cv': a_cv,
                    'start_char': a_char,
                    'end_cv': b_cv,
                    'end_char': b_char,
                    'year': year,
                    'anime_name': name,
                    'weight': weight
                })
            except:
                continue
    with open(EDGE_INFO, encoding='utf-8', mode='w') as f:
        json.dump(edge_dic, f, ensure_ascii=False, indent=2)


def get_cv_dic(database):
    cv_dic = {}
    for anime in database:
        for info in anime['cast']:
            try:
                charactor, cv = format_info(info)
                if cv not in cv_dic:
                    cv_dic[cv] = VoiceActor(cv)
            except:
                continue
    return cv_dic


def generate_graph(cv_dic, database):
    g = networkx.MultiGraph()
    g.add_nodes_from(cv_dic.values())
    for anime in database:
        for a, b in combinations(anime['cast'], 2):
            try:
                _, a_cv = format_info(a)
                _, b_cv = format_info(b)
                g.add_edge(cv_dic[a_cv], cv_dic[b_cv],
                           anime_name=anime['name'], weight=get_weight(anime['cast'], a, b))
            except:
                continue

    networkx.write_gpickle(g, GRAPH_PATH)

    return g


def get_pos(g):
    pos_dic = networkx.drawing.layout.spring_layout(g, dim=2, scale=5e4)
    with open(POS_INFO, encoding='utf-8', mode='w') as f:
        for item in pos_dic:
            pos_info = "{} {} {}\n".format(item, *pos_dic[item])
            f.write(pos_info)
"""
def temp():
    tempg = networkx.Graph()
    VA_LIST = ['丰崎爱生', '内田真礼', '日笠阳子', '花泽香菜']
    tempg.add_nodes_from(VA_LIST)
    pos_dic = networkx.drawing.layout.spring_layout(tempg, dim=3, scale=10000)
    with open(POS_INFO, encoding='utf-8', mode='w') as f:
        for item in pos_dic:
            f.write(item.name)
            f.write(' ')
            f.write(str(pos_dic[item][0]))
            f.write(' ')
            f.write(str(pos_dic[item][1]))
            f.write(' ')
            f.write(str(pos_dic[item][2]))
            f.write('\n')
"""


def net_info(cv_dic):
    MAIN_URL = 'https://zh.moegirl.org/'

    def getHTMLcontent(cv_name):
        url = MAIN_URL + cv_name + '#'
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            return r.content
        except:
            print(cv_name + 'fail getHTMLcontent')
            return None

    def download_picture(url, save_route):
        try:
            r = requests.get(url)
            r.raise_for_status()
        except:
            return 'fail downloadpicture'
        with open(save_route, 'wb') as f:
            f.write(r.content)

    def save_intro(text, save_route):
        with open(save_route, 'w+', encoding="utf-8") as f:
            f.write(text)

    def parse_website(cv_name, html):
        if html is not None:
            soup = BeautifulSoup(html, 'html.parser')
        try:
            table = soup.find('table', {'class': 'infobox'})
            image = table.findChild('img')
            img_url = image.attrs['src']
            intro = table.findNextSibling()
            if intro.text != '' and intro.name == 'p':
                text = intro.text
            else:
                text = intro.findNextSibling('p').text
            cv_route = "{}/{}".format(INTRODUCTION_ROUTE, cv_name)
            cv_image_route = "{}/{}.jpg".format(cv_route, cv_name)
            cv_intro_route = "{}/{}.txt".format(cv_route, cv_name)
            if not os.path.exists(cv_route):
                os.makedirs(cv_route)
            download_picture(img_url, cv_image_route)
            save_intro(text, cv_intro_route)
            print(cv_name, "success")
        except Exception as e:
            print(e)
            print(cv_name + "fail parse_website")

    for cv in cv_dic:
        content = getHTMLcontent(cv)
        parse_website(cv, content)


def compute_centrality(g, cv_dic):
    betweenness_centrality = networkx.centrality.betweenness_centrality(
        g, weight="weight")
    closeness_centrality = networkx.centrality.closeness_centrality(
        g, weight='weight')
    for cv in betweenness_centrality:
        cv.betweenness_centrality = betweenness_centrality[cv]
        cv.closeness_centrality = closeness_centrality[cv]
    with open(CENTRALITY_INTO, 'w') as f:
        json.dump(cv_dic, f, indent=2, encoding="utf-8")


def test():
    database = get_data(SAVE_FILE)
    to_json(database)
    """
    if os.path.exists(GRAPH_PATH):
        g = networkx.read_gpickle(GRAPH_PATH)
    else:
    """
    """
    g = generate_graph(cv_dic, database)
    # print(networkx.is_connected(g))

    print(networkx.shortest_path(
        g, cv_dic['阿澄佳奈'], cv_dic['松冈祯丞'], weight='weight'))
    print(networkx.dijkstra_path_length(
        g, cv_dic['阿澄佳奈'], cv_dic['松冈祯丞'], weight='weight'))

    #tree = networkx.algorithms.tree.mst.minimum_spanning_edges(g, weight='weight')
    #total_weight = sum((item[3]['weight'] for item in tree))
    print(len(g.nodes))
    # net_info(cv_dic)g

    # get_pos(cv_dic)

    # to_json(database)
    """
test()
