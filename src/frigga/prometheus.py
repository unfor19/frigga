import json
import requests
from time import time

from bs4 import BeautifulSoup
import yaml

from .config import print_msg


def request_words(url, selector, replace_str="()", replace_with=""):
    response = requests.get(url)
    if 200 <= response.status_code < 400:
        print_msg(
            msg_content=f"Successfully got words from {url}", msg_type='log')
    else:
        print_msg(
            msg_content=f"Failed to reach {url}, have you provided the '--web.enable-admin-api' in Prometheus?"  # noqa: 501
        )
    html_page_text = response.text
    soup = BeautifulSoup(html_page_text, 'html.parser')
    return [
        item.string.replace(replace_str, replace_with)
        for item in soup.select(selector)
    ]


def get_ignored_words():
    """Get the list of words to ignore when scraping from Grafana"""
    print_msg(
        msg_content="Getting the list of words to ignore when scraping from Grafana"  # noqa: 501
    )
    words_list = []

    prometheus_urls = [
        {
            "url": "https://prometheus.io/docs/prometheus/latest/querying/functions/",  # noqa: 501
            "selectors": ".toc-right ul li code"
        },
        {
            "url": "https://prometheus.io/docs/prometheus/latest/querying/operators/",  # noqa: 501
            "selectors": "ul li code"
        }
    ]
    for item in prometheus_urls:
        words_list += request_words(item["url"], item["selectors"])
    return sorted(list(set(words_list)))


def apply_yaml(prom_yaml_path, metrics_json_path, create_backup_file=True, skip_rules_file=False):  # noqa: 501
    print_msg(msg_content=f"Reading documents from {prom_yaml_path}")
    with open(prom_yaml_path, "r") as fp:
        prom_yaml = fp.read()
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
            msg_content="Missing 'scrape_configs' in prometheus.yml",
            msg_type="error"
        )
    if not frigga_doc:
        print_msg(
            msg_content="Missing frigga document in prometheus.yml",
            msg_type="error"
        )
    print_msg(msg_content="Found relevant documents")
    print_msg(msg_content="Loading metrics.json")
    with open(metrics_json_path, "r") as file:
        metrics_dict = json.load(file)

    print_msg(msg_content="Generating metrics_relabel_configs in memory")
    relabel_configs = []
    for metric in metrics_dict['all_metrics']:
        relabel_configs.append({
            "source_labels": ['__name__'],
            "regex": f"^{metric}",
            "target_label": "__tmp_keep_me",
            "replacement": True
        })
    relabel_configs.append({
        "source_labels": ["__tmp_keep_me"],
        "regex": True,
        "action": "keep"
    })

    noalias_dumper = yaml.dumper.SafeDumper
    noalias_dumper.ignore_aliases = lambda self, data: True

    # write relabel configs to file
    if not skip_rules_file:
        rules_file_path = ".prometheus-rules.yml"
        print_msg(
            msg_content=f"Writing relabel_configs to {rules_file_path}")
        with open(rules_file_path, 'w') as fs:
            yaml.dump_all(
                documents=[relabel_configs],
                stream=fs, default_flow_style=False,
                Dumper=noalias_dumper,
                indent=2
            )

    # add relabel configs to all jobs, except the ones in exclude_jobs
    for job in prom_doc['scrape_configs']:
        if job['job_name'] not in frigga_doc['exclude_jobs']:
            job['metric_relabel_configs'] = relabel_configs

    # backup old prom yaml
    if create_backup_file:
        print_msg(msg_content=f"Creating a backup file for {prom_yaml_path}")
        with open(prom_yaml_path, 'r') as source_fs:
            with open("prometheus.yml.bak.yml", 'w') as target_fs:
                target_fs.write(source_fs.read())

    # write new prom frigga yaml
    print_msg(
        msg_content=f"Writing the new metrics_relabel_configs to {prom_yaml_path}"  # noqa: 501
    )
    with open(prom_yaml_path, 'w') as fs:
        yaml.dump_all(
            documents=[prom_doc, frigga_doc],
            stream=fs, default_flow_style=False,
            Dumper=noalias_dumper,
            indent=2
        )
    msg = f"Done! Now reload {prom_yaml_path} with 'frigga pr -u http://localhost:9090'"  # noqa: 501
    print_msg(msg_content=msg)
    return msg


def reload_prom(prom_url="http://localhost:9090", raw=False):
    api_path = "/-/reload"
    url = f"{prom_url}{api_path}"
    response = requests.post(url, allow_redirects=True)
    if 200 <= response.status_code < 204:
        data = response.status_code
        if raw:
            print(data)
            return data
        else:
            print_msg(
                msg_content=f"Successfully reloaded Prometheus - {url}",
                msg_type='log'
            )
            return {
                "status": data,
                "prom_url": url
            }
    else:
        print_msg(
            msg_content=f"Failed to reload Prometheus - {url}, have you provided the '--web.enable-admin-api' in Prometheus?",  # noqa:501
            msg_type='error',
            data=response.text
        )
    return True


def get_total_dataseries(prom_url="http://localhost:9090", raw=False):
    api_path = "/api/v1/query"
    target_url = f"{prom_url}{api_path}"
    query = "sum(scrape_samples_post_metric_relabeling)"
    timestamp = int(time())
    query_string_parameters = f"query={query}&start={timestamp}"
    url = f"{target_url}?{query_string_parameters}"

    try:
        response = requests.get(url, allow_redirects=True)
    except Exception as error:
        print_msg(
            msg_content=error.__str__(),
            msg_type='error'
        )
    if 200 <= response.status_code < 204:
        try:
            resp = response.json()
            data = int(resp['data']['result'][0]['value'][1])
        except Exception as e:
            print_msg(
                msg_content=f"Unknown response\n{e}",
                data=resp,
                msg_type="error"
            )
        if raw:
            print(data)
            return data
        else:
            print_msg(
                msg_content=f"Total number of data-series: {data}",
                msg_type='log'
            )
            return {"num_data_series": data}
    else:
        print_msg(
            msg_content=f"Failed to get total number of data-series. Is Prometheus reachable? - {url}",  # noqa:501
            msg_type='error',
            data=response.text
        )
    return True
