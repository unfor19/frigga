#!/bin/bash
set -e
set -o pipefail

# Modify if necessary
target_url=${1:-"http://localhost:9090"}
api_path="/api/v1/query"
query="sum(scrape_samples_post_metric_relabeling)"

# Computed
timestamp=$(date +%s)
query_string_parameters="query=${query}&start=${timestamp}"
api_url="${target_url}/${api_path}?${query_string_parameters}"

# Result
curl -sL "$api_url" | jq -r .data.result[].value[1]