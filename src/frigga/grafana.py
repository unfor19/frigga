import json
import re
import requests
from .config import scrape_value_by_key, print_msg
from .prometheus import get_ignored_words


def grafana_http_request(path, api_key, base_url="http://localhost:3000"):
    if not api_key:
        print_msg(msg_content="Missing API Key",
                  msg_type='error', terminate=True)
    url = f"{base_url}{path}"
    response = requests.get(url, headers={
        "Authorization": f"Bearer {api_key}"
    })
    if 200 <= response.status_code < 400:
        print_msg(
            msg_content=f"Successful response from {url}", msg_type='log')
        return response
    if response.status_code == 401:
        print_msg("API Key is invalid", response.text,
                  'error')
    else:
        print_msg("Unknown response", response.text, 'error')
    return response


def get_metrics_from_expr(expression, ignored_words_list):
    # Remove all [] and {}
    regex_patterns = [
        r"\{(.+?)\}",
        r"\[(.+?)\]",
    ]
    for pattern in regex_patterns:
        results = re.findall(pattern, expression)
        if results:
            results = list(set(results))
            results = [
                result.strip() for result in results
                if result and result != " "
            ]
            for result in results:
                expression = expression.replace(result, " ")

    # Remove all the ignored_words
    for item in ignored_words_list:
        pattern = r"[\(\)\{\}]" + item + r"[ \(\)\{\}]"
        results = re.findall(pattern, expression)
        if results:
            results = list(set(results))
            results = [
                result.strip() for result in results
                if result and result != " "
            ]
            for result in results:
                expression = expression.replace(result, " ")

    # Remove leftovers
    # TODO: Avoid this loop, cleanup in previous step
    math_signs = ["*", "-", "+", "^", "/", "]",
                  "[", "{", "}", "__", ",", "=", "\\", "'", '"', "_over_time"]
    for sign in math_signs:
        expression = expression.replace(sign, " ")
    metrics = expression.split()

    return metrics


def get_metrics_list(base_url, api_key, output_file_path=".metrics.json"):
    ignored_words = get_ignored_words()
    if len(ignored_words):
        print_msg(
            msg_content=f"Found {len(ignored_words)} words to ignore in expressions"  # noqa: 501
        )
    else:
        print_msg(msg_content="No words to ignore, that's weird",
                  msg_type="warning")

    try:
        dashboards = grafana_http_request(
            "/api/search?query=",
            api_key,
            base_url
        )
    except Exception as error:
        print_msg(
            msg_content=error.__str__(),
            msg_type="error"
        )

    dashboards = dashboards.json()
    data = {
        "dashboards": dict()
    }
    for dashboard in dashboards:
        dashboard_body = grafana_http_request(
            f"/api/dashboards/uid/{dashboard['uid']}",
            api_key,
            base_url
        ).json()
        dashboard_gnetid = dashboard_body['dashboard']['gnetId'] \
            if 'gnetId' in dashboard_body['meta'] and dashboard_body['meta']['gnetId'] else "null"  # noqa: 501
        dashboard_name = dashboard_body['meta']['slug'] \
            if 'slug' in dashboard_body['meta'] and dashboard_body['meta']['slug'] else "null"  # noqa: 501
        print_msg(msg_content=f"Getting metrics from {dashboard_name}")
        expressions = \
            scrape_value_by_key(dashboard_body, "expr", str, []) \
            + scrape_value_by_key(dashboard_body, "query", str, [])
        dashboard_metrics = []
        for expression in expressions:
            try:
                expr_metrics = get_metrics_from_expr(expression, ignored_words)
            except TypeError:
                print_msg(msg_content="The following expression is corrupted",
                          data=expression, msg_type='e')
            if expr_metrics:
                for metric in expr_metrics:
                    try:
                        float(metric)
                    except:  # noqa: 722
                        if len(metric) > 5 and "/" not in metric:
                            dashboard_metrics.append(metric)
        dashboard_metrics = sorted(list(set(dashboard_metrics)))
        data['dashboards'][dashboard_name] = dict()
        data['dashboards'][dashboard_name]['metrics'] = dashboard_metrics
        data['dashboards'][dashboard_name]['gnet_id'] = dashboard_gnetid
        data['dashboards'][dashboard_name]['num_metrics'] = len(
            dashboard_metrics)
        print_msg(
            msg_content=f"Found {data['dashboards'][dashboard_name]['num_metrics']} metrics"  # noqa: 501
        )

    all_metrics = []
    for dashboard_name in data['dashboards']:
        all_metrics += data['dashboards'][dashboard_name]['metrics']
    data['all_metrics'] = sorted(list(set(all_metrics)))
    data['all_metrics_num'] = len(data['all_metrics'])
    print_msg(
        msg_content=f"Found a total of {data['all_metrics_num']} unique metrics to keep"  # noqa: 501
    )

    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=2, sort_keys=True)

    return data
