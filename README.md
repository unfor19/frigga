# frigga

[![testing](https://github.com/unfor19/frigga/workflows/testing/badge.svg?branch=master)](https://github.com/unfor19/frigga/actions?query=workflow%3Atesting)

Scrape only relevant metrics in Prometheus, according to your Grafana dashboards, see the [before and after snapshot](https://snapshot.raintank.io/dashboard/snapshot/p4YmuKHu4jBlA2kPmOhbuda3jo4I51bt?orgId=2).

This tool extermely useful for [Grafana Cloud](https://grafana.com/products/cloud/) customers, since the pricing is per DataSeries ingestions.

## Requirements

Python 3.6.7+

## Installation

```bash
$ pip install frigga
```

## Getting Started

1. Grafana - Import the dashboard [frigga - Jobs Usage](docker-compose/grafana/provisioning/dashboards/jobs-usage.json) (ID: 12537) to Grafana, and check out your current number of DataSeries
1. Grafana - Generate an API Key for `Viewer`
1. Get the list of metrics that are used in your dasboards

   ```bash
   $ frigga gl # gl is grafana-list, or good luck :)

   Grafana url [http://localhost:3000]: http://my-grafana.grafana.net
   Grafana api key: (hidden)
   >> [LOG] Getting the list of words to ignore when scraping from Grafana
   ...
   >> [LOG] Found a total of 269 unique metrics to keep
   ```

   `.metrics.json` - automatically generated in pwd

   ```json
   {
       "all_metrics": [
           "cadvisor_version_info",
           "container_cpu_usage_seconds_total",
           "container_last_seen",
           "container_memory_max_usage_bytes",
           ...
       ]
   }
   ```

1. Edit your `prometheus.yml` file, add the following snippet to the bottom of the file. Check the example in [docker-compose/prometheus-original.yml](docker-compose/prometheus-original.yml)

   ```yml
    ---
    name: frigga
    exclude_jobs: []
   ```

1. Use the `.metrics.json` file to apply the rules to your existing `prometheus.yml`

   ```bash
   $ frigga pa # pa is prometheus-apply, or pam-tada-dam

   Prom yaml path [docker-compose/prometheus.yml]: /etc/prometheus/prometheus.yml
   Metrics json path [./.metrics.json]: /home/willywonka/.metrics.json
   >> [LOG] Reading documents from docker-compose/prometheus.yml
   ...
   >> [LOG] Done! Now reload docker-compose/prometheus.yml with 'docker exec $PROM_CONTAINER_NAME kill -HUP 1'
   ```

1. As mentioned in the previous step, reload the `prometheus.yml` to Prometheus, here are two ways of doing it
   - "Kill" Prometheus
     ```bash
     $ docker exec $PROM_CONTAINER_NAME kill -HUP 1
     ```
   - Send a POST request to `/-/reload` - this requires Prometheus to be loaded with `--web.enable-lifecycle`, for example, see [docker-compose.yml](docker-compose/docker-compose.yml)
     ```bash
     $ curl -X POST http://localhost:9090/-/reload
     ```
1. Make sure the `prometheus.yml` was loaded successfully to Prometheus

   ```bash
   $ docker logs --tail 10 $PROM_CONTAINER_NAME

    level=info ts=2020-06-27T15:45:34.514Z caller=main.go:799 msg="Loading configuration file" filename=/etc/prometheus/prometheus.yml
    level=info ts=2020-06-27T15:45:34.686Z caller=main.go:827 msg="Completed loading of configuration file" filename=/etc/prometheus/prometheus.yml
   ```

1. Grafana - Now check `frigga - Jobs Usage` dashboard, the numbers should be signifcantly lower (up to 60% or even more)

## Test it locally

### Requirements

1. [Docker](https://docs.docker.com/get-docker/)
1. [docker-compose](https://docs.docker.com/compose/install/)
1. [jq](https://stedolan.github.io/jq/download/)

### Getting Started

1. git clone this repository
1. Deploy locally the services: Prometheus, Grafana, node-exporter and cadvisor

   ```bash
   $ bash docker-compose/deploy_stack.sh

   Creating network frigga_net1
   ...
   >> Grafana - Generating API Key - for Viewer
   eyJrIjoiT29hNGxGZjAwT2hZcU1BSmpPRXhndXVwUUE4ZVNFcGQiLCJuIjoibG9jYWwiLCJpZCI6MX0=
   # Save this key ^^^
   ```

1. Open your browser, navigate to http://localhost:3000

   - Username and password are admin:admin
   - You'll be prompted to update your password, so just keep using `admin` or hit Skip

1. Go to [Jobs Usage](http://localhost:3000/d/U9Se3uZMz/jobs-usage?orgId=1) dashboard, you'll see that Prometheus is processing ~2800 DataSeries
1. Get all the metrics that are used in your Grafana dasboards

   ```bash
   $ frigga gl -gurl http://localhost:3000 -gkey $GRAFANA_API_KEY

   >> [LOG] Getting the list of words to ignore when scraping from Grafana
   ...
   >> [LOG] Found a total of 269 unique metrics to keep
   # Generated .metrics.json in pwd
   ```

1. Apply the rules to `prometheus.yml`, keep the defaults

   ```bash
   $ frigga pa # prometheus-apply

   Prom yaml path [docker-compose/prometheus.yml]:
   Metrics json path [./.metrics.json]:
   ...
   >> [LOG] Done! Now reload docker-compose/prometheus.yml with 'docker exec $PROM_CONTAINER_NAME kill -HUP 1'
   ```

1. Reload `prometheus.yml` to Prometheus

   ```bash
   $ bash docker-compose/reload_prom_config.sh show

   >> Reloading prometheus.yml configuration file
   ...
   level=info ts=2020-06-27T16:25:17.656Z caller=main.go:827 msg="Completed loading of configuration file" filename=/etc/prometheus/prometheus.yml
   ```

1. Go to [Jobs Usage](http://localhost:3000/d/U9Se3uZMz/jobs-usage?orgId=1), you'll see that Prometheus is processing only ~1000 DataSeries (previously ~2800)
   - In case you don't see the change, don't forget to hit the refersh button
1. Cleanup
   ```bash
   $ docker-compose -p frigga --file docker-compose/docker-compose.yml down
   ```

## Pros and Cons of this tool

### Pros

1. [Grafana-Cloud](https://grafana.com/products/cloud/) - As a Grafana Cloud customer, the main reason for writing this tool was lowering the costs. This goal was achieved by sending only the relevant DataSeries to Grafana Cloud
negligible
1. Saves disk-space on the machine running Prometheus
1. Improves PromQL performance by querying less metrics; significant only when processing high volumes

### Cons

1. After applying the rules in `prometheus.yml`, it makes the file less readable. Due to the fact it's not a file that you play with on a daily basis, it's okayish
1. The memory usage of Prometheus increases slightly, around ~30MB, not significant, but worth mentioning
1. If you intend to use more metrics, for example, you've added a new dashboard which uses more metrics, you'll need to do the same process again; `frigga gl` and `frigga pa`

## References
- [metric_relabel_configs](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#metric_relabel_configs)
- [Or in relabelling](https://www.robustperception.io/or-in-relabelling)
- [relabel_configs vs metrics_relabel_configs](https://www.robustperception.io/relabel_configs-vs-metric_relabel_configs)


## Authors

Created and maintained by [Meir Gabay](https://github.com/unfor19)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/unfor19/frigga/blob/master/LICENSE) file for details
