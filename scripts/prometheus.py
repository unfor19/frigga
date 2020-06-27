import json
import requests
from bs4 import BeautifulSoup
import yaml
from .config import print_json, print_msg


def request_words(url, selector, replace_str="()", replace_with=""):
    response = requests.get(url)
    if 200 <= response.status_code < 400:
        print_msg(
            msg_content=f"Successfully got words from {url}", msg_type='log')
    else:
        print_msg(
            msg_content=f"Failed to reach {url}, have you provided the '--web.enable-admin-api' in Prometheus?")
    html_page_text = response.text
    soup = BeautifulSoup(html_page_text, 'html.parser')
    return [
        item.string.replace(replace_str, replace_with)
        for item in soup.select(selector)
    ]


def get_ignored_words():
    """Get the list of words to ignore when scraping from Grafana"""
    print_msg(
        msg_content="Getting the list of words to ignore when scraping from Grafana")
    words_list = []

    prometheus_urls = [
        {
            "url": "https://prometheus.io/docs/prometheus/latest/querying/functions/",
            "selectors": ".toc-right ul li code"
        },
        {
            "url": "https://prometheus.io/docs/prometheus/latest/querying/operators/",
            "selectors": "ul li code"
        }
    ]
    for item in prometheus_urls:
        words_list += request_words(item["url"], item["selectors"])
    return sorted(list(set(words_list)))


def apply_yaml(prom_yaml_path, metrics_json_path, create_backup_file=True):
    print_msg(msg_content=f"Reading documents from {prom_yaml_path}")
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
    if not prom_doc:
        print_msg(
            msg_content="Missing 'scrape_configs' in prometheus.yml", msg_type="error")
    if not frigga_doc:
        print_msg(
            msg_content="Missing frigga document in prometheus.yml", msg_type="error")
    print_msg(msg_content=f"Found relevant documents")
    print_msg(msg_content=f"Loading metrics.json")
    with open(metrics_json_path, "r") as file:
        metrics_dict = json.load(file)

    print_msg(msg_content=f"Generating metrics_relabel_configs in memory")
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
    if create_backup_file:
        print_msg(msg_content=f"Creating a backup file for {prom_yaml_path}")
        with open(prom_yaml_path, 'r') as source_fs:
            with open(f"{prom_yaml_path}.bak.yml", 'w') as target_fs:
                target_fs.write(source_fs.read())

    # write new prom frigga yaml
    print_msg(
        msg_content=f"Writing the new metrics_relabel_configs to {prom_yaml_path}")
    with open(prom_yaml_path, 'w') as fs:
        data = yaml.dump_all(
            documents=[prom_doc, frigga_doc],
            stream=fs, default_flow_style=False,
            Dumper=noalias_dumper,
            indent=2
        )
    print_msg(
        msg_content=f"Done! Now reload {prom_yaml_path} with 'docker exec $PROM_CONTAINER_NAME kill -HUP 1'")
