import json
import click
from .grafana import get_metrics_list
from .config import print_msg
from .prometheus import apply_yaml


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        app_aliases = {
            "m": "main",
            "p": "prometheus",
            "g": "grafana",
        }
        action_aliases = {
            "a": "apply",
            "g": "get",
            "d": "delete",
            "l": "list",
        }
        if len(cmd_name) == 2:
            words = []
            if cmd_name[0] in app_aliases:
                words.append(app_aliases[cmd_name[0]])
            if cmd_name[1] in action_aliases:
                words.append(action_aliases[cmd_name[1]])
            if len(words) == 2:
                cmd_name = "-".join(words)

        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")


# @click.group()
@ click.command(cls=AliasedGroup)
@click.option('--ci', '-ci', is_flag=True, help="Use this flag to avoid deletion confirmation prompts")  # noqa: E501
def cli(ci):
    """Test"""  # noqa: E501
    pass


@cli.command()
@click.option('--grafana-url', '-gurl', default='http://localhost:3000', prompt=True, required=False, show_default=True, type=str)
@click.option('--grafana-api-key', '-gkey', prompt=True, required=True, hide_input=True, type=str)
@click.option('--output-file-path', '-o', default='./.metrics.json', show_default=True, required=False, type=str)
# @click.option('--file', '-f', prompt=False, default=".", help="Output metrics.json file to pwd")
def grafana_list(grafana_url, grafana_api_key, output_file_path):
    """Provide Grafana UrL and Grafana API Key (Viewer)\n
Returns a list of metrics that are used in all dashboards"""
    if "http" not in grafana_url:
        print_msg(
            msg_content="Grafana URL must contain 'http' or 'https'", msg_type="error")
    metrics = get_metrics_list(grafana_url, grafana_api_key)
    with open(output_file_path, 'w') as file:
        json.dump(metrics, file, indent=2, sort_keys=True)


@cli.command()
@click.option('--prom-yaml-path', '-ppath', default='docker-compose/prometheus.yml', prompt=True, required=True, show_default=False, type=str)
@click.option('--metrics-json-path', '-mjpath', default='./.metrics.json', show_default=True, prompt=True, required=False, type=str)
@click.option('--create-backup-file', '-b', is_flag=True, default=True, required=False)
def prometheus_apply(prom_yaml_path, metrics_json_path, create_backup_file):
    apply_yaml(prom_yaml_path, metrics_json_path, create_backup_file)
