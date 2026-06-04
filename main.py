import argparse
import configparser
import json
import os
from concurrent.futures import ThreadPoolExecutor

import requests


class Website:
    def __init__(self, name, port=None, path=None, url=None, python_env=None):
        self.name = name
        self.port = port
        self.url = url
        self.path = path
        self.python_env = python_env
        self.status_code = None
        self.reason = None
        self.elapsed = None
        self.error = None

    def as_dict(self):
        return {
            "name": self.name,
            "url": get_url(self),
            "status_code": self.status_code,
            "reason": self.reason,
            "elapsed_seconds": self.elapsed,
            "error": self.error,
        }


def get_url(website):
    if not website.url and not website.port:
        raise ValueError("Website '{}' is missing both port and url".format(website.name))
    if website.url and website.port:
        return "{}:{}".format(website.url.rstrip("/"), website.port)
    if website.url:
        return website.url
    return "http://localhost:{}".format(website.port)


def check_online(website, timeout=5):
    url = get_url(website)
    try:
        response = requests.get(url, timeout=timeout)
        website.status_code = response.status_code
        website.reason = response.reason
        website.elapsed = response.elapsed.total_seconds()
    except requests.exceptions.RequestException as error:
        website.error = str(error)
    return website


def ingest_data(file="websites.ini"):
    config = configparser.ConfigParser()
    read_files = config.read(file)
    if not read_files:
        raise FileNotFoundError("Config file not found: {}".format(file))

    websites = []
    for section in config.sections():
        websites.append(
            Website(
                name=section,
                port=config[section].get("port") or None,
                url=config[section].get("url") or None,
                path=config[section].get("path") or None,
                python_env=config[section].get("python_env") or None,
            )
        )
    return websites


def check_all(websites, timeout=5, workers=4):
    max_workers = max(1, min(workers, len(websites) or 1))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(lambda site: check_online(site, timeout=timeout), websites))


def main():
    parser = argparse.ArgumentParser(description="Check configured website uptime.")
    parser.add_argument(
        "--config",
        default=os.environ.get("UPTIME_CONFIG", "websites.ini"),
        help="Path to INI config. Defaults to UPTIME_CONFIG or websites.ini.",
    )
    parser.add_argument("--timeout", type=float, default=5, help="Request timeout in seconds")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent worker count")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    websites = ingest_data(args.config)
    results = check_all(websites, timeout=args.timeout, workers=args.workers)

    if args.json:
        print(json.dumps([site.as_dict() for site in results], indent=2))
    else:
        for site in results:
            data = site.as_dict()
            print(
                "{name} {url} status={status_code} reason={reason} error={error}".format(
                    **data
                )
            )


if __name__ == "__main__":
    main()
