import json
import requests
from bs4 import BeautifulSoup


def request_words(url, selector, replace_str="()", replace_with=""):
    html_page_text = requests.get(url).text
    soup = BeautifulSoup(html_page_text, 'html.parser')
    return [
        item.string.replace(replace_str, replace_with)
        for item in soup.select(selector)
    ]


def get_ignored_words():
    """Get the list of words to ignore when scraping from Grafana"""
    words_list = []

    with open("data.json", "r") as file:
        data_file = json.load(file)
    for item in data_file["data"]["prometheus_urls"]:
        words_list += request_words(item["url"], item["selectors"])
    return sorted(list(set(words_list)))
