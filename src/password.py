import base64

import requests
import json

import time

import argparse

HEADERS = {
    'Content-Type': 'application/json',
    'Connection': 'close',
    'User-Agent': 'aspen%20production/2618 CFNetwork/758.3.15 Darwin/15.4.0',
    'Content-Encoding': 'identity',
    'Accept': '*/*',
    'Accept-Language': 'en-us',
}

URL = "https://{host}:443/umi"


def get_password(host):
    url = URL.format(host=host)
    HEADERS["Host"] = host

    for rid in range(1, 120):
        time.sleep(1)
        payload = {"do": "get", "args": ["passwd"], "id": rid}
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload), verify=False)
        if response.status_code == 200:
            result = json.loads(response.text)
            if "ok" not in result:
                continue
            return result["ok"]["passwd"], rid
    return None, -1


def get_blid(passwd, host, rid):
    b64_pass = base64.b64encode("user:{}".format(passwd).encode()).decode()

    url = URL.format(host=host)
    HEADERS["Host"] = host
    HEADERS["Authorization"] = "Basic {}".format(b64_pass)

    payload = {"do": "get", "args": ["sys"], "id": rid}
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload), verify=False)
    if response.status_code == 200:
        result = json.loads(response.text)
        blid = result["ok"]["blid"]
        blid = [str(hex(x + 0x10000))[5:] for x in blid]
        return "".join(blid)


def run(args):
    password, processing_id = get_password(args.host)
    if not password:
        print("Timeout")
    print("passwd:{}".format(password))
    blid = get_blid(password, args.host, processing_id)
    print("blid:{}".format(blid))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Python Controller for iRobot Roomba 9xx")
    parser.add_argument("host", action="store", nargs=None, const=None, default=None, type=str, choices=None,
                        help="IP address of your robot")
    run(parser.parse_args())
