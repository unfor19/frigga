import asyncio
import websockets
import json

from .prometheus import get_total_dataseries as prometheus_get
from .grafana import get_metrics_list as grafana_list
from .prometheus import apply_yaml as prometheus_apply
from .prometheus import reload_prom as prometheus_reload


async def msg(websocket, path):
    received = await websocket.recv()
    try:
        received = json.loads(received)
    except Exception:
        print("simple text")

    print(f"Requested: {received}")
    message = ""
    if 'action' in received:
        if received['action'] == "prometheus_get":
            received.pop('action')
            message = prometheus_get(**received)
        elif received['action'] == "grafana_list":
            received.pop('action')
            message = grafana_list(**received)
            message = "Created .metrics.json!"
        elif received['action'] == "prometheus_apply":
            received.pop('action')
            message = prometheus_apply(**received)
        elif received['action'] == "prometheus_reload":
            received.pop('action')
            message = prometheus_reload(**received)
    else:
        message = f"Hello {received}!"
    message = json.dumps(message)
    await websocket.send(message)
    print(f"Sent back: {message}")


def run_wss(port=8084, debug=False):
    start_server = websockets.serve(msg, "0.0.0.0", port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    run_wss()
