# frigga

Get the Prometheus metrics that are used on a Grafana instance.

## Features

- [x] Get metrics list from Grafana
- [ ] Produce a `prometheus.yml` with rules, according to Grafana's metrics list

## Requirements

Python 3.6.7+

## Installation

```bash
$ pip install frigga
```

## Getting Started

```bash
$ frg get-metrics
Grafana url: http://localhost:3000
Grafana api key: (hidden)
...
[
    metrics list
]
```

## Benefits from this tool

<details><summary>
Expand/Collapse</summary>

1. [Grafana-Cloud](https://grafana.com/products/cloud/) - the main reason for writing this tool, which lowers the costs due to minimizing the number of active-series
1. Lowers CPU consumption and memory usage of Prometheus
1. Saves disk-space on the machine running Prometheus
1. Reduces network traffic when using `remote_write`
1. Improves PromQL performance by querying less metrics

</details>
