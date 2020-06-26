import re
import requests
from .config import scrape_value_by_key
from .prometheus import get_ignored_words


def grafana_http_request(path, api_key, base_url="http://localhost:3000"):
    if not api_key:
        print("ERROR: Need to create '.apikey' file")
        exit()
    url = f"{base_url}{path}"
    return requests.get(url, headers={
        "Authorization": f"Bearer {api_key}"
    })


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
        pattern = r"[ \(\)\{\}]" + item + r"[ \(\)\{\}]"
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
    math_signs = ["*", "-", "+", "^", "/", "]", "[", "{", "}"]
    for sign in math_signs:
        expression = expression.replace(sign, " ")
    metrics = expression.split()
    return metrics


def get_metrics_list(base_url, api_key):
    ignored_words = get_ignored_words()
    dashboards = grafana_http_request(
        "/api/search?query=",
        api_key,
        base_url
    ).json()
    data = {
        "dashboards": {}
    }
    for dashboard in dashboards:
        dashboard_body = grafana_http_request(
            f"/api/dashboards/uid/{dashboard['uid']}",
            api_key,
            base_url
        ).json()
        expressions = scrape_value_by_key(dashboard_body, "expr")
        dashboard_metrics = []
        for expression in expressions:
            expr_metrics = get_metrics_from_expr(expression, ignored_words)
            if expr_metrics:
                for metric in expr_metrics:
                    try:
                        float(metric)
                    except:  # noqa: 722
                        if len(metric) > 5 and "/" not in metric:
                            dashboard_metrics.append(metric)
        dashboard_metrics = list(set(dashboard_metrics))
        dashboard_metrics.sort()
        dashboard_name = dashboard_body['meta']['slug']
        dashboard_gnetid = dashboard_body['dashboard']['gnetId']
        data['dashboards'][dashboard_name] = dict()
        data['dashboards'][dashboard_name]['metrics'] = dashboard_metrics
        data['dashboards'][dashboard_name]['gnet_id'] = dashboard_gnetid
        data['dashboards'][dashboard_name]['num_metrics'] = len(
            dashboard_metrics)
    return data
