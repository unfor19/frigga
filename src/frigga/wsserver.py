import asyncio
import websockets
import json
import logging

from .prometheus import get_total_dataseries as prometheus_get
from .grafana import get_metrics_list as grafana_list
from .prometheus import apply_yaml as prometheus_apply
from .prometheus import reload_prom as prometheus_reload

logging.basicConfig()
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)


async def msg(websocket, path):
    received = await websocket.recv()
    try:
        received = json.loads(received)
    except Exception:
        pass

    print(f"Requested: {received}")
    message = ""
    if 'action' in received:
        try:
            if received['action'] == "prometheus_get":
                received.pop('action')
                message = prometheus_get(**received)
                message = f">> [LOG] Current number of metrics - {message}"
            elif received['action'] == "grafana_list":
                received.pop('action')
                message = grafana_list(**received)
                message = f">> [LOG] Successfully created {received['output_file_path']}"  # noqa: 501
            elif received['action'] == "prometheus_apply":
                received.pop('action')
                message = prometheus_apply(**received)
                message = ">> [LOG] Successfully applied new relabel rules in Prometheus. Reload Prometheus to apply the changes."  # noqa: 501
            elif received['action'] == "prometheus_reload":
                received.pop('action')
                message = prometheus_reload(**received)
                message = ">> [LOG] Successfully reloaded Prometheus"
        except Exception as error:
            logger.error(error)
            await websocket.close(code=1011, reason=error.__str__()[0:120])

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
