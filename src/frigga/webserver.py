from .prometheus import reload_prom as prometheus_reload
from .prometheus import apply_yaml as prometheus_apply
from .prometheus import get_total_dataseries as prometheus_get
from .grafana import get_metrics_list as grafana_list
import logging

from flask import Flask, request
from flask_restful import reqparse, Resource, Api
from waitress import serve


app = Flask(__name__)
api = Api(app)


class GrafanaList(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('base_url')
        parser.add_argument('api_key')
        args = parser.parse_args()
        data = grafana_list(base_url=args['base_url'], api_key=args['api_key'])
        return data, 200


class PrometheusGet(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('prom_url')
        parser.add_argument('raw')
        args = parser.parse_args()
        data = prometheus_get(**args)
        logger = logging.getLogger('waitress')
        logger.info(data)
        return data, 200


class PrometheusApply(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('prom_yaml_path')
        parser.add_argument('metrics_json_path')
        parser.add_argument('create_backup_file')
        parser.add_argument('skip_rules_file')
        args = parser.parse_args()
        data = prometheus_apply(**args)
        return data, 200


class PrometheusReload(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('prom_url')
        parser.add_argument('raw')
        args = parser.parse_args()
        data = prometheus_reload(**args)
        return data, 200


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


class WebserverStop(Resource):
    def post(self):
        shutdown_server()
        return 'frigga webserver is shutting down...', 200


def run(port=8083, debug=False):
    api.add_resource(WebserverStop, '/stop')
    api.add_resource(GrafanaList, '/grafana/list')
    api.add_resource(PrometheusGet, '/prometheus/get')
    api.add_resource(PrometheusApply, '/prometheus/apply')
    api.add_resource(PrometheusReload, '/prometheus/reload')
    logging.basicConfig()
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    run()
