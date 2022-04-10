from bs4 import BeautifulSoup
import requests
import re
import os
import time
mdir = os.path.join(os.path.dirname(__file__), 'automated')
"testing"
test_url = "https://nhentai.to/g/386602"
class BaseExtractor(object):
    BASE_URL = "https://nhentai.to"
    RANDOM_URL = "https://nhentai.to/random/"
    TAGS_URL = "https://nhentai.to/tags/"
    ARTISTS_URL = "https://nhentai.to/artists/"
    CHARACTERS_URL = "https://nhentai.to/characters/"
    PARODIES_URL = "https://nhentai.to/parodies/"
    GROUPS_URL = "https://nhentai.to/groups/"
    

    def parse_page_data(self, type=str):
        _image_links = list()
        html = requests.get(self.RANDOM_URL)
        soup = BeautifulSoup(html.content, 'lxml')        
        _id = re.findall(r"/([0-9].+)", html.url)[0]
        print("Title: {0}".format((soup.find("h1").text)))
        print("ID: {0}".format(_id))
        containers = soup.find_all("div", "thumb-container")
        
        for image in containers:
            _image_link = image.find("a", "gallerythumb").get('href')
            _full_link = self.BASE_URL + _image_link
            _image_links.append(_full_link)
        
        
        for link in _image_links:
            _direct_link = ""
            _count = 0
            try:
                while True:
                    html = requests.get(link).content
                    soup = BeautifulSoup(html, "lxml")
                    if soup.find('title').text == "nhentai.to | 504: Gateway time-out":
                        print("Gateway Timeout...Retrying.")
                        time.sleep(2)
                        continue
                    if soup.find("img", "fit-horizontal").get('src') != None:
                        print("Element found.")
                        _direct_link = soup.find("img", "fit-horizontal").get('src')
                        break
                    
                with requests.get(_direct_link, stream=True) as r:
                    r.raise_for_status()
                    name = re.findall(r".+/([0-9].+.[a-z].+)", _direct_link)[0]
                    with open(os.path.join(mdir, name), "wb") as f:
                        for chunk in r.iter_content(chunk_size=256):
                            if chunk:
                                f.write(chunk)
                    time.sleep(2)
                    
            except requests.exceptions.HTTPError:
                print('HTTP Error. Retrying...')
                time.sleep(2)
                continue
            finally:
                print("Downloaded {0} out of --- images.")

debug = BaseExtractor()
debug.parse_page_data()
