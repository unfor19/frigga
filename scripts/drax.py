import click
from .grafana import get_metrics_list
from .config import print_json


@click.group()
@click.option('--ci', '-ci', is_flag=True, help="Use this flag to avoid deletion confirmation prompts")  # noqa: E501
def cli(ci):
    """Test"""  # noqa: E501
    pass


@cli.command()
@click.option('--grafana-url', '-gurl', prompt=True)
@click.option('--grafana-api-key', '-gkey', prompt=True, hide_input=True)
def get_metrics(grafana_url, grafana_api_key):
    """Provide Grafana UrL and Grafana API Key (Viewer)\n
Returns a list of metrics that are used in all dashboards"""
    if "http" not in grafana_url:
        raise Exception("Must contain 'http' or 'https'")
    metrics = get_metrics_list(grafana_url, grafana_api_key)
    print_json(metrics)
