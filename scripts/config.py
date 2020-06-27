import json
import os


def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )


def print_msg(msg_content, data=None, msg_type='l', terminate=False):
    if msg_type == "data" or msg_type == "d":
        msg = f">> {msg_content}\nData:\n"
    elif msg_type == "error" or msg_type == "e":
        msg = f">> [ERROR] {msg_content}"
        terminate = True
    elif msg_type == "warning" or msg_type == "w":
        msg = f">> [WARNING] {msg_content}"
    elif msg_type == "log" or msg_type == "l":
        msg = f">> [LOG] {msg_content}"

    if data:
        if isinstance(data, dict) or isinstance(data, list):
            print(f"{msg}\n{json.dumps(data, indent=2, sort_keys=True)}")
        else:
            print(f"{msg} {data}")
    else:
        print(msg)

    if terminate:
        exit()


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
