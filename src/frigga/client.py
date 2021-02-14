from os import environ as env
import requests
from time import sleep


frigga_url = env['FRIGGA_URL'] if 'FRIGGA_URL' in env else "http://localhost:8083"  # noqa: 501
prom_url = env['PROM_URL'] if 'PROM_URL' in env else "http://localhost:9090"
prom_yaml_path = env['PROM_YAML_PATH'] if 'PROM_YAML_PATH' in env else "docker-compose/prometheus.yml"  # noqa: 501
metrics_json_path = env['METRICS_JSON_PATH'] if 'METRICS_JSON_PATH' in env else ".metrics.json"  # noqa: 501
create_back_file = env['CREATE_BACKUP_FILE'] if 'CREATE_BACKUP_FILE' in env else True  # noqa: 501
skip_rules_file = env['SKIP_RULES_FILE'] if 'SKIP_RULES_FILE' in env else False  # noqa: 501
grafana_url = env['GRAFANA_URL'] if 'GRAFANA_URL' in env else "http://localhost:3000"  # noqa: 501
grafana_api_key = env['GRAFANA_API_KEY'] if 'GRAFANA_API_KEY' in env else None  # noqa: 501
sleep_seconds = float(env['SLEEP_SECONDS']) if 'SLEEP_SECONDS' in env else 15  # noqa: 501


def prometheus_get():
    api_path = "/prometheus/get"
    url = f"{frigga_url}{api_path}"
    resp = requests.get(
        url=url,
        params={
            "prom_url": prom_url,
            "raw": True
        }
    )
    if resp.status_code == 200:
        data = int(resp.text)
        return data
    else:
        return resp.text


def grafana_list():
    api_path = "/grafana/list"
    url = f"{frigga_url}{api_path}"
    resp = requests.post(
        url=url,
        data={
            "base_url": grafana_url,
            "api_key": grafana_api_key,
            "output_file_path": metrics_json_path
        },
        timeout=15
    )
    data = resp.text
    return data


def prometheus_apply():
    api_path = "/prometheus/apply"
    url = f"{frigga_url}{api_path}"
    resp = requests.post(
        url=url,
        data={
            "prom_yaml_path": prom_yaml_path,
            "metrics_json_path": metrics_json_path,
            "create_backup_file": create_back_file,
            "skip_rules_file": skip_rules_file
        }
    )
    data = resp.text
    return data


def prometheus_reload():
    api_path = "/prometheus/reload"
    url = f"{frigga_url}{api_path}"
    resp = requests.post(url=url, data={
        "prom_url": prom_url,
        "raw": True
    })
    data = resp.text
    return data


def main():
    num_dataseries_before = prometheus_get()
    print(num_dataseries_before)
    metrics_json = grafana_list()
    print(metrics_json)
    prom_apply_results = prometheus_apply()
    print(prom_apply_results)
    prom_reload_results = prometheus_reload()
    print(prom_reload_results)
    print(f"Sleeping for {sleep_seconds} seconds ...")
    sleep(sleep_seconds)
    num_dataseries_after = prometheus_get()
    print(num_dataseries_after)
    if num_dataseries_after < num_dataseries_before:
        decreased_precentage = round(
            100 * (1 - (num_dataseries_after/num_dataseries_before)), 2)
        print(
            f"decreased from {num_dataseries_before} to {num_dataseries_after}, {decreased_precentage}%"  # noqa: 501
        )
    elif num_dataseries_after == num_dataseries_before:
        print(f"no change - {num_dataseries_after}")
    else:
        raise Exception("something went wrong")


if __name__ == '__main__':
    main()
