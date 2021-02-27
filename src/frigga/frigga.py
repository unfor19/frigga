import click


from .grafana import get_metrics_list
from .config import print_msg, is_docker, pass_config
from .prometheus import apply_yaml, reload_prom, get_total_dataseries
from .webserver import run as run_webserver
from .client import main as run_client
from .wsserver import run_wss as run_websocket_webserver
from .wsclient import main as run_websocket_client


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        app_aliases = {
            "c": "client",
            "m": "main",
            "p": "prometheus",
            "g": "grafana",
            "w": "webserver"
        }
        action_aliases = {
            "a": "apply",
            "g": "get",
            "d": "delete",
            "l": "list",
            "r": "reload",
            "s": "start"
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


@click.command(cls=AliasedGroup)
@pass_config
@click.option(
    '--ci', '-ci',
    is_flag=True, help="Use this flag to avoid confirmation prompts"
)
def cli(config, ci):
    """No confirmation prompts"""
    if is_docker():
        ci = True
    config.ci = ci


@cli.command()
@click.option(
    '--grafana-url', '-gurl',
    default='http://localhost:3000',
    prompt=True, required=False, show_default=True, type=str
)
@click.option(
    '--grafana-api-key', '-gkey',
    prompt=True, required=True, hide_input=True, type=str)
@click.option(
    '--output-file-path', '-o',
    default='./.metrics.json',
    show_default=True, required=False, type=str
)
def grafana_list(grafana_url, grafana_api_key, output_file_path):
    """Alias: gl\n
Provide Grafana URL and Grafana API Key (Viewer)\n
Returns a list of metrics that are used in all dashboards"""
    if "http" not in grafana_url:
        print_msg(
            msg_content="Grafana URL must contain 'http' or 'https'",
            msg_type="error"
        )
    get_metrics_list(grafana_url, grafana_api_key, output_file_path)


@cli.command()
@click.option(
    '--prom-yaml-path',
    '-ppath',
    default='docker-compose/prometheus.yml',
    prompt=True, required=True, show_default=False, type=str
)
@click.option(
    '--metrics-json-path', '-mjpath',
    default='./.metrics.json',
    show_default=True, prompt=True, required=False, type=str
)
@click.option(
    '--create-backup-file', '-b',
    is_flag=True, default=True, required=False
)
@click.option(
    '--skip-rules-file', '-sr',
    is_flag=True, default=False, required=False
)
def prometheus_apply(prom_yaml_path, metrics_json_path, create_backup_file, skip_rules_file):  # noqa: 501
    """Alias: pa\n
Applies .metrics.json for a given prometheus.yml file\n

By default:\n
- Creates a backup of prometheus.yml to prometheus.yml.bak.yml (same dir as prometheus.yml)\n
- Creates a .prometheus-rules.yml file with all relabel_configs
    """  # noqa: 501
    apply_yaml(prom_yaml_path, metrics_json_path,
               create_backup_file, skip_rules_file)


@cli.command()
@click.option(
    '--prom-url', '-u',
    default='http://localhost:9090',
    prompt=True, required=True, show_default=False, type=str
)
@click.option(
    '--raw', '-r',
    is_flag=True, default=False, required=False
)
def prometheus_reload(prom_url, raw):
    """Alias: pr\n
    Reload Prometheus
    """
    reload_prom(prom_url, raw)


@cli.command()
@click.option(
    '--prom-url', '-u',
    default='http://localhost:9090',
    prompt=True, required=True, show_default=False, type=str
)
@click.option(
    '--raw', '-r',
    is_flag=True, default=False, required=False
)
def prometheus_get(prom_url, raw):
    """Alias: pg\n
    Get total number of data series
    """
    get_total_dataseries(prom_url, raw)


@cli.command()
@click.option(
    '--debug', '-d',
    is_flag=True,
    prompt=False, required=False, type=int
)
@click.option(
    '--port', '-p',
    default=8084,
    prompt=False, required=False, type=int
)
@click.option(
    '--use-http',
    is_flag=True,
    default=False,
    prompt=False, required=False
)
def webserver_start(debug, port, use_http):
    """Alias: ws\n
Runs a webserver that will execute frigga's commands, according to the client's requests\n
The webserver should have network access to Grafana and Prometheus instances, and read/write permission to the prometheus.yml file.\n
By default:\n
- Runs as a WebSockets server, to use an HTTP server, add the `--use-http` flag
    """  # noqa: 501
    if not use_http:
        run_websocket_webserver(port, debug)
    else:
        run_webserver(port, debug)


@cli.command()
@click.option(
    '--prom-url', '-u',
    default='http://localhost:9090',
    required=False, type=str
)
@click.option(
    '--raw', '-r',
    is_flag=True, default=False, required=False
)
@click.option(
    '--metrics-json-path', '-mjpath',
    default='./.metrics.json',
    required=False, type=str
)
@click.option(
    '--create-backup-file', '-b',
    is_flag=True, default=True, required=False
)
@click.option(
    '--skip-rules-file', '-sr',
    is_flag=True, default=False, required=False
)
@click.option(
    '--grafana-url', '-gurl',
    default='http://localhost:3000',
    required=False, type=str
)
@click.option(
    '--frigga-url', '-gurl',
    default='ws://localhost:8084',
    required=False, type=str
)
@click.option(
    '--grafana-api-key', '-gkey',
    required=False, type=str)
@click.option(
    '--output-file-path', '-o',
    default='./.metrics.json',
    required=False, type=str
)
@click.option(
    '--prom-yaml-path',
    '-ppath',
    default='prometheus.yml',
    required=False, type=str
)
@click.option(
    '--use-http',
    is_flag=True,
    default=False,
    prompt=False, required=False
)
def client_start(use_http, **kwargs):
    """Alias: cs\n
    Runs a WebSockets client, to use HTTP, add `--use-http`\n
    - Order of commands- prometheus-get (before change), grafana-list, prometheus-apply, prometheus-get (after change)\n
    - Priority of args:\n
    client arguments > client env vars > server arguments > server env vars"""  # noqa: 501

    if not use_http:
        run_websocket_client(kwargs)
    else:
        run_client(kwargs)


@cli.command()
def version():
    """Print the installed version"""
    from .__init__ import __version__ as version
    print(version)
