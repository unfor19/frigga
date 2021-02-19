from os import environ as env

import asyncio
import websockets
import json
from time import sleep

frigga_url = env['FRIGGA_URL'] if 'FRIGGA_URL' in env else "ws://localhost:8084"  # noqa: 501
prom_url = env['PROM_URL'] if 'PROM_URL' in env else "http://localhost:9090"
prom_yaml_path = env['PROM_YAML_PATH'] if 'PROM_YAML_PATH' in env else "docker-compose/prometheus.yml"  # noqa: 501
metrics_json_path = env['METRICS_JSON_PATH'] if 'METRICS_JSON_PATH' in env else ".metrics.json"  # noqa: 501
create_backup_file = env['CREATE_BACKUP_FILE'] if 'CREATE_BACKUP_FILE' in env else True  # noqa: 501
skip_rules_file = env['SKIP_RULES_FILE'] if 'SKIP_RULES_FILE' in env else False  # noqa: 501
grafana_url = env['GRAFANA_URL'] if 'GRAFANA_URL' in env else "http://localhost:3000"  # noqa: 501
grafana_api_key = env['GRAFANA_API_KEY'] if 'GRAFANA_API_KEY' in env else None  # noqa: 501
sleep_seconds = float(env['SLEEP_SECONDS']) if 'SLEEP_SECONDS' in env else 15  # noqa: 501


async def start_websocket():
    num_dataseries_before = await send_message({
        "action": "prometheus_get",
        "prom_url": prom_url,
        "raw": True
    })

    await send_message({
        "action": "grafana_list",
        "base_url": grafana_url,
        "api_key": grafana_api_key,
        "output_file_path": metrics_json_path
    })

    await send_message({
        "action": "prometheus_apply",
        "prom_yaml_path": prom_yaml_path,
        "metrics_json_path": metrics_json_path,
        "create_backup_file": create_backup_file,
        "skip_rules_file": skip_rules_file
    })

    await send_message({
        "action": "prometheus_reload",
        "prom_url": prom_url,
        "raw": True
    })

    print("Sleeping 10 seconds ...")
    sleep(10)

    num_dataseries_after = await send_message({
        "action": "prometheus_get",
        "prom_url": prom_url,
        "raw": True
    })

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


async def send_message(message="empty"):
    uri = frigga_url
    async with websockets.connect(uri) as websocket:

        await websocket.send(json.dumps(message))

        response = await websocket.recv()
        try:
            response = json.loads(response)
        except Exception:
            pass
        print(f"{response}")
        return response


def main():
    asyncio.get_event_loop().run_until_complete(asyncio.gather((start_websocket())))  # noqa: 501


if __name__ == '__main__':
    main()
