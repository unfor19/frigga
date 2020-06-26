import json
import click
from .grafana import get_metrics_list
from .config import print_json


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        aliases = {
            "m": "metrics",
            "a": "apply",
            "g": "get",
            "d": "delete",
            "l": "list",
        }
        if len(cmd_name) == 2:
            words = [aliases[char] for char in cmd_name if char in aliases]
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
@click.option('--grafana-url', '-gurl', prompt=True)
@click.option('--grafana-api-key', '-gkey', prompt=True, hide_input=True)
# @click.option('--file', '-f', prompt=False, default=".", help="Output metrics.json file to pwd")
def metrics_get(grafana_url, grafana_api_key):
    """Provide Grafana UrL and Grafana API Key (Viewer)\n
Returns a list of metrics that are used in all dashboards"""
    if "http" not in grafana_url:
        raise Exception("Must contain 'http' or 'https'")
    metrics = get_metrics_list(grafana_url, grafana_api_key)
    print_json(metrics)
    with open('.metrics.json', 'w') as file:
        json.dump(metrics, file, indent=2, sort_keys=True)
