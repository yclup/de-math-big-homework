from parse_data import get_data, SAVE_FILE
from selenium import webdriver
import re
import time
import json
import os

TOTALSUM = 0
TOTALNUM = 0

BASE_URL = "https://baike.baidu.com"


def get_results_number(wd, driver):  # 以下三个函数用来获得动漫在百度百科中的浏览记录条数以反映其重要程度
    try:
        inputbox = driver.find_element_by_id("query")
        if inputbox is None:
            driver.get(BASE_URL)
            inputbox = driver.find_element_by_id("query")
        inputbox.clear()
        inputbox.send_keys(wd)
        search = driver.find_element_by_id("search")
        search.click()
        time.sleep(1)
        try:
            num_text = driver.find_element_by_id("j-lemmaStatistics-pv")
        except:
            try:
                href = driver.find_element_by_xpath(
                    "//div[@class='para']/a[1]")
                driver.get(href.get_attribute("href"))
                time.sleep(1)
                num_text = driver.find_element_by_id("j-lemmaStatistics-pv")
            except:
                try:
                    driver.get(driver.find_element_by_class_name(
                        'result-title').get_attribute("href"))
                    time.sleep(1)
                    num_text = driver.find_element_by_id(
                        "j-lemmaStatistics-pv")
                except:
                    print("anime_name" + wd + "failed")
                    return "-1"
    except:
        driver.get(BASE_URL)
        return "-1"
    num = num_text.text
    return num


def add_results_number():
    global TOTALSUM, TOTALNUM
    database = get_data(SAVE_FILE)
    driver = webdriver.Firefox()
    driver.get(BASE_URL)
    for anime in database:
        try:
            anime['score'] = get_results_number(format(anime['name']), driver)
            print("{}, OK, score: {}".format(anime['name'], anime['score']))
            TOTALNUM += 1
            TOTALSUM += float(anime['score'])
        except:
            continue

    average = TOTALSUM / TOTALNUM
    for anime in database:
        if anime['score'] == "-1":
            anime['score'] = str(average)
    print("average: {}".format(TOTALSUM / TOTALNUM))
    with open(SAVE_FILE, encoding='utf-8', mode='w') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)


def format(anime_name):
    formatted_name = ""
    for char in anime_name:
        if char != '(' and char != '（' and char != '第':
            formatted_name += char
        else:
            break
    return formatted_name


def fix_average():
    database = get_data(SAVE_FILE)
    for anime in database:
        if anime["score"] == "":
            anime["score"] = "1000"
        if float(anime["score"]) > 1e7:
            print(anime["name"])

fix_average()
