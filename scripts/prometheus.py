import json
import requests
from bs4 import BeautifulSoup
import yaml
from .config import print_json


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


def create_yaml():
    prom_yaml_path = "docker-swarm/prometheus.yml"
    metrics_path = ".metrics.json"
    with open(prom_yaml_path, "r") as file:
        prom_yaml = file.read()
    prom_documents = yaml.safe_load_all(prom_yaml)
    prom_doc = None
    frigga_doc = None
    for doc in prom_documents:
        if 'scrape_configs' in doc:
            prom_doc = doc
        elif 'name' in doc and doc['name'] == 'frigga':
            frigga_doc = doc
    if not prom_doc or not frigga_doc:
        print("not good")
        exit()
    with open(metrics_path, "r") as file:
        metrics_dict = json.load(file)

    metric_relabel_configs = []
    for metric in metrics_dict['all_metrics']:
        metric_relabel_configs.append({
            "source_labels": ['__name__'],
            "regex": f"^{metric}",
            "target_label": "__tmp_keep_me",
            "replacement": True
        })
    metric_relabel_configs.append({
        "source_labels": ["__tmp_keep_me"],
        "regex": True,
        "action": "keep"
    })
    for job in prom_doc['scrape_configs']:
        if job['job_name'] not in frigga_doc['exclude_jobs']:
            job['metric_relabel_configs'] = metric_relabel_configs

    noalias_dumper = yaml.dumper.SafeDumper
    noalias_dumper.ignore_aliases = lambda self, data: True

    # backup old prom yaml
    with open(prom_yaml_path, 'r') as source_fs:
        with open(f"{prom_yaml_path}.bak.yml", 'w') as target_fs:
            target_fs.write(source_fs.read())

    # write new prom frigga yaml
    with open(prom_yaml_path, 'w') as fs:
        data = yaml.dump_all(
            documents=[prom_doc, frigga_doc],
            stream=fs, default_flow_style=False,
            Dumper=noalias_dumper,
            indent=2
        )
