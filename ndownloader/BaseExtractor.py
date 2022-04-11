from bs4 import BeautifulSoup
import requests
import urllib3
import http
import re
import os
import time
from fake_useragent import UserAgent




test_url = "https://nhentai.to/g/386602"
class BaseExtractor(object):
    def __init__(self):
        pass


    BASE_URL = "https://nhentai.to"
    RANDOM_URL = "https://nhentai.to/random/"
    GALLERY_URL = "https://nhentai.to/g/"
    
    
    SEARCH_URL = "https://nhentai.to/search?"
    TAGS_URL = "https://nhentai.to/tags/"
    ARTISTS_URL = "https://nhentai.to/artists/"
    CHARACTERS_URL = "https://nhentai.to/characters/"
    PARODIES_URL = "https://nhentai.to/parodies/"
    GROUPS_URL = "https://nhentai.to/groups/"
    mdir = os.path.join(os.path.dirname(__file__), 'automated')

    # Scrape images from one page
    ###########################################   
    def _scrape_images_from_page(self, url=None):
        _image_links = list()
        invalid_chars = f'<>:"\/|?*'
        pattern = r'[' + invalid_chars + ']'
        
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml')        
        _id = re.findall(r"/([0-9].+)", html.url)[0]
        title = soup.find("h1").text
        print("Title: {0}".format(title))
        print("ID: {0}".format(_id))
        containers = soup.find_all("div", "thumb-container")
        print("Number of images: {0}".format(len(containers)))
        new_name = re.sub(pattern, ' ', title)[:155]
        
        if os.path.exists(os.path.join(self.mdir, new_name)):
            print("Gallery directory exists.")
        else:
            os.mkdir(os.path.join(self.mdir, new_name))
            print('Gallery directory created.')
        
        self.mdir = os.path.join(self.mdir, new_name)
            
        for image in containers:
            _image_link = image.find("a", "gallerythumb").get('href')
            _full_link = self.BASE_URL + _image_link
            _image_links.append(_full_link)

        self._get_gallery(gallery_list=_image_links)
        
    
    # Scrape galleries from page
    ####################################
    def scrape_galleries_from_page(self, url=None, pages=None, per_page=None):
        # if int(pages) > 100:
        #     raise ValueError("'pages' parameter must not exceed 100.")
        
        
        gallery__links = list()
        # if int(pages) == 1 or pages is None:
        #     print("Scraping only the first page.")
        #     html = requests.get(url).content
        #     soup = BeautifulSoup(html, 'lxml')
        #     galleries = soup.find_all('div', "gallery")
        #     pages = soup.find("a", "next").find_previous_sibling("a").text
        #     print("Number of pages: {0}".format(pages))
        #     print("Number of galleries in page: {0}".format(len(galleries)))
            
        #     for gallery in galleries:
        #         gallery_link = gallery.find("a", "cover").get("href")
        #         link = self.BASE_URL + gallery_link
        #         gallery__links.append(link)
            
        for page in range(1, (pages + 1)) if pages is not None else (range(1, 2)):
            print("page: {0}".format(page))
            augmented_url = url + "page={0}".format(page)
            print("link augmented: {0}".format(augmented_url))
            html = requests.get(augmented_url).content
            soup = BeautifulSoup(html, 'lxml')
            galleries = soup.find_all('div', 'gallery')
            print("Number of galleries in page: {0}".format(len(galleries)))
            
            for gallery in galleries[:per_page] if per_page is not None else galleries:
                gallery_link = gallery.find("a", "cover").get("href")
                link = self.BASE_URL + gallery_link
                gallery__links.append(link)
        
        
        print(len(gallery__links))
        return gallery__links
        
                
        
        
        
    def _get_gallery(self, gallery_list=None):
        _count = 0
        for link in gallery_list:
            _direct_link = ""
            while True:
                try:   
                    html = requests.get(link).content
                    soup = BeautifulSoup(html, "lxml")
                    print(soup)
                    if soup.find('title').text == "nhentai.to | 504: Gateway time-out":
                        print("Gateway Timeout Error...Retrying.")
                        time.sleep(2)
                        continue
                    if soup.find('title').text == "nhentai.to | 520: Web server is returning an unknown error":
                        print("520: Server just hit a wall...Retrying in 2 second(s)")
                        time.sleep(2)
                        continue
                    if soup.find("img", "fit-horizontal").get('src') != None:
                        print("Image Element found.")
                        _direct_link = soup.find("img", "fit-horizontal").get('src')
                        with requests.get(_direct_link, stream=True, timeout=5) as r:
                            r.raise_for_status()
                            name = re.findall(r".+/([0-9].+.[a-z].+)", _direct_link)[0]
                            with open(os.path.join(self.mdir, name), "wb") as f:
                                for chunk in r.iter_content():
                                    if chunk:
                                        f.write(chunk)  
                    break
                                  
                except requests.exceptions.HTTPError:
                    print('HTTP Error. Retrying...')
                    continue
                except requests.exceptions.Timeout as TimeOutError:
                    print('Taking too long...trying again')
                    continue
                except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError) as e:
                    print("connection aborted. waiting for {0} second(s) and trying again.".format(2))
                    time.sleep(3)
                    continue
            _count += 1
    