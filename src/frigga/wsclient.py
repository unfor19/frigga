from os import environ as env

import asyncio
import websockets
import json
from time import sleep

from .config import print_msg

sleep_seconds = float(env['SLEEP_SECONDS']) if 'SLEEP_SECONDS' in env else 30  # noqa: 501


async def start_websocket(kwargs):
    num_dataseries_before = await send_message({
        "action": "prometheus_get",
        "prom_url": kwargs['prom_url'],
        "raw": kwargs['raw'],
        "frigga_url": kwargs['frigga_url'],
    })

    await send_message({
        "action": "grafana_list",
        "base_url": kwargs['grafana_url'],
        "api_key": kwargs['grafana_api_key'],
        "output_file_path": kwargs['metrics_json_path'],
        "frigga_url": kwargs['frigga_url'],
    })

    await send_message({
        "action": "prometheus_apply",
        "prom_yaml_path": kwargs['prom_yaml_path'],
        "metrics_json_path": kwargs['metrics_json_path'],
        "create_backup_file": kwargs['create_backup_file'],
        "skip_rules_file": kwargs['skip_rules_file'],
        "frigga_url": kwargs['frigga_url'],
    })

    await send_message({
        "action": "prometheus_reload",
        "prom_url": kwargs['prom_url'],
        "raw": True,
        "frigga_url": kwargs['frigga_url'],
    })
    print_msg(msg_content=f"Sleeping {sleep_seconds} seconds ...")
    sleep(sleep_seconds)

    num_dataseries_after = await send_message({
        "action": "prometheus_get",
        "prom_url": kwargs['prom_url'],
        "raw": True,
        "frigga_url": kwargs['frigga_url']
    })

    num_dataseries_before = int(
        num_dataseries_before.__str__().split("-")[1].strip())
    num_dataseries_after = int(
        num_dataseries_after.__str__().split("-")[1].strip())

    if num_dataseries_after < num_dataseries_before:
        decreased_precentage = round(
            100 * (1 - (num_dataseries_after/num_dataseries_before)), 2)
        print_msg(
            f"Successfully decreased from {num_dataseries_before} to {num_dataseries_after}, {decreased_precentage}%"  # noqa: 501
        )
    elif num_dataseries_after == num_dataseries_before:
        print_msg(f"No change - {num_dataseries_after}")
    else:
        print(f">> [ERROR] Before ({num_dataseries_before}) is smaller than after ({num_dataseries_after})")  # noqa: 501
        exit(1)


async def send_message(kwargs):
    uri = kwargs['frigga_url']
    if 'frigga_url' in kwargs:
        kwargs.pop('frigga_url')
    async with websockets.connect(uri) as websocket:

        await websocket.send(json.dumps(kwargs))
        response = None
        try:
            response = await websocket.recv()
        except Exception as error:
            print(error)
            exit()

        try:
            response = json.loads(response)
        except Exception:
            pass

        print(f"{response}")
        return response


def main(kwargs):
    asyncio.get_event_loop().run_until_complete(asyncio.gather((start_websocket(kwargs))))  # noqa: 501


if __name__ == '__main__':
    main()
