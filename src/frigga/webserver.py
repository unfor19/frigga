import logging

from flask import Flask, request, jsonify
from waitress import serve

from .prometheus import reload_prom as prometheus_reload
from .prometheus import apply_yaml as prometheus_apply
from .prometheus import get_total_dataseries as prometheus_get
from .grafana import get_metrics_list as grafana_list


app = Flask(__name__)


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


@app.route('/grafana/list', methods=['POST', ])
def list_grafana_metrics():
    args = {
        "base_url": request.form['base_url'],
        "api_key": request.form['api_key'],
        "output_file_path": request.form['output_file_path']
    }
    try:
        grafana_list(**args)
    except Exception as e:
        internal_server_error(e)
    return f"Created {args['output_file_path']}"


@app.route('/prometheus/get', methods=['GET'])
def get_prometheus_dataseries_num():
    args = {
        "prom_url": request.args.get('prom_url'),
        "raw": request.args.get('raw')
    }
    try:
        data = prometheus_get(**args)
    except Exception as e:
        internal_server_error(e)

    logging.basicConfig()
    logger = logging.getLogger('waitress')
    logger.info(data)
    return str(data)


@app.route('/prometheus/apply', methods=['POST', ])
def apply_prometheus():
    args = {
        "prom_yaml_path": request.form['prom_yaml_path'],
        "metrics_json_path": request.form['metrics_json_path'],
        "create_backup_file": request.form['create_backup_file'],
        "skip_rules_file": request.form['skip_rules_file']
    }
    try:
        data = prometheus_apply(**args)
    except Exception as e:
        internal_server_error(e)

    print(data)
    return data


@app.route('/prometheus/reload', methods=['POST', ])
def reload_prometheus():
    args = {
        "prom_url": request.form['prom_url'],
        "raw": request.form['raw']
    }
    data = prometheus_reload(**args)
    print(data)
    return "reloaded"


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/stop', methods=['POST', ])
def webserver_stop():
    shutdown_server()
    return 'frigga webserver is shutting down...'


def run(port=8083, debug=False):
    serve(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    run()
