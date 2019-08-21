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
        self.response = None
        self.status_code = None
        self.reason = None
        self.elapsed = None
        self.BadExcept = None

    def print(self):
        try:
            print("name:", self.name, end=" ")
        except KeyError:
            pass
        try:
            print("port:", self.port, end=" ")
        except KeyError:
            pass
        try:
            print("url:", self.url, end=" ")
        except KeyError:
            pass
        try:
            print("response:", self.response, end=" ")
        except (KeyError, AttributeError):
            pass
        try:
            print("status_code:", self.status_code, end=" ")
        except (KeyError, AttributeError):
            pass
        try:
            print("reason:", self.reason, end=" ")
        except (KeyError, AttributeError):
            pass
        try:
            print("elapsed:", self.elapsed, end=" ")
        except (KeyError, AttributeError):
            pass
        try:
            print("BadExcept:", self.BadExcept, end=" ")
        except (KeyError, AttributeError):
            pass
        print("")

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
        website.BadExcept = False
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        website.BadExcept = True
        pass
    return website


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


def wrapMyFunc(index, website):
    return [index, check_online(website)]

def update(results):
    index = results[0]
    new_website = results[1]
    # note: input comes from async `wrapMyFunc`
    processed_websites[index] = new_website  # put answer into correct index of result list
    pbar.update()


print("Ingesting data")
websites = ingest_data()
# start processing the websites
print("start processing the websites")
processes = len(websites)
pbar = tqdm.tqdm(total=len(websites))
processed_websites = [None] * len(websites) # result list of correct size


with Pool(processes) as p:
    for i in range(len(websites)):
        p.apply_async(wrapMyFunc, args=(i, websites[i]), callback=update)
    p.close()
    p.join()
    pbar.close()



for i in processed_websites:
    boi = i
    i.print()
