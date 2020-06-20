import json
import os


def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )


def print_json(obj):
    print(json.dumps(obj, indent=2, sort_keys=True))


def scrape_value_by_key(obj, search_key, my_list=[]):
    """Provide and obj and key to search
Returns a list of values, according to given key"""
    if isinstance(obj, list) and len(obj):
        for item in obj:
            scrape_value_by_key(item, search_key, my_list)
    elif isinstance(obj, dict):
        if search_key in obj and obj[search_key]:
            return my_list.append(obj[search_key])
        else:
            for key, value in obj.items():
                if (isinstance(value, list) or isinstance(value, dict)):
                    scrape_value_by_key(value, search_key, my_list)
    return my_list
