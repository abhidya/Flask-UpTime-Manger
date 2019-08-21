import requests
import configparser
import threading
import tqdm
from multiprocessing import Pool

class Website:
    def __init__(self, name, port, url=None):
        self.name = name
        self.port = port
        self.url = url

    def print(self):
        try:
            print(self.name)
        except KeyError:
            pass
        try:
            print(self.port)
        except KeyError:
            pass
        try:
            print(self.url)
        except KeyError:
            pass
        try:
            print(self.response)
        except KeyError:
            pass
        try:
            print(self.status_code)
        except KeyError:
            pass
        try:
            print(self.reason)
        except KeyError:
            pass
        try:
            print(self.elapsed)
        except KeyError:
            pass
        try:
            print(self.RequestException)
        except KeyError:
            pass

def get_url(website):
    url = website.url
    port = website.port
    if url is None and port is None:
        website.print()
        raise Exception('Website Missing Port and URL info in config')
    if url is None:
        return "http://localhost:" + port
    else:
        return url + ":" + port


def check_online(website):
    url = get_url(website)
    try:
        response = requests.get(url)
        website.response = response
        website.status_code = response.status_code
        website.reason = response.reason
        website.time = response.elapsed
        website.RequestException = False
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        website.response = None
        website.status_code = None
        website.reason = None
        website.time = None
        website.RequestException = True

def ingest_data(file="websites.ini"):
    config = configparser.ConfigParser()
    config.read(file)
    websites = []
    for i in config.sections():
        name = i
        port = config[i]["port"]
        url = config[i]["url"]
        websites.append(Website(name=name, port=port, url=url))
    return websites


def run_item(f, item):
    result_info = [threading.Event(), None]

    def runit():
        result_info[1] = f(item)
        result_info[0].set()

    threading.Thread(target=runit).start()
    return result_info


def gather_results(result_infos):
    results = []
    for i in range(len(result_infos)):
        result_infos[i][0].wait()
        results.append(result_infos[i][1])
    return results


# def process(website):
processes = 8
print("Ingesting data")
websites = ingest_data()
# start processing the websites
print("start processing the websites")

pool = Pool(processes=processes)
for _ in tqdm.tqdm(pool.imap_unordered(check_online, websites), total=len(websites)):
    pass


for i in websites:
    boi = i
    i.print()
