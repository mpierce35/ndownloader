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
    def __init__(self, dirname=None):
        self.BASE_DIR = dirname if dirname is not None else self._create_init_directory()
        self.categories = {
            "artist" : "https://nhentai.to/artist/",
            "tag": "https://nhentai.to/tag/",
            "character" : "https://nhentai.to/character/",
            "parody": "https://nhentai.to/parody/",
            "group": "https://nhentai.to/group/"
        }


    BASE_URL = "https://nhentai.to/"
    RANDOM_URL = "https://nhentai.to/random/"
    GALLERY_URL = "https://nhentai.to/g/"
    TAGS_URL = "https://nhentai.to/tag/"
    SEARCH_URL = "https://nhentai.to/search?"
    ARTISTS_URL = "https://nhentai.to/artist/"
    CHARACTERS_URL = "https://nhentai.to/characters/"
    PARODIES_URL = "https://nhentai.to/parodies/"
    GROUPS_URL = "https://nhentai.to/groups/"
    mdir = os.path.join(os.path.dirname(__file__), 'automated')
    
    # Create directory when creating an instance
    ############################################
    
    def _create_init_directory(self):
        default_dir = os.path.join(os.path.dirname(__file__), 'automated')
        if os.path.exists(default_dir) == False:
            os.mkdir(default_dir)
            print('Default directory created.')
        else:
            print('Default directory exists.')
        
        return default_dir
        
    
    def _create_gallery_directory(self, dirname=None):
        newdir = os.path.join(self.BASE_DIR, dirname)[:155]
        if os.path.exists(newdir) == False:
            os.mkdir(newdir)

        return newdir 

    # Scrape images from one page
    ###########################################   
    def _scrape_images_from_page(self, url=None):
        _image_links = list()
        invalid_chars = f'<>:"\/|?*().'
        pattern = r'[' + invalid_chars + ']'
        
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml')        
        _id = re.findall(r"/([0-9].+)", html.url)[0]
        title = soup.find("h1").text
        containers = soup.find_all("div", "thumb-container")
        print("Title: {0}".format(title))
        print("ID: {0}".format(_id))
        print("Number of images: {0}".format(len(containers)))
        x = re.sub(pattern, '', title)
        new_name = f"{_id}-{x}"[:150]
        for image in containers:
            _image_link = image.find("a", "gallerythumb").get('href')
            _full_link = self.BASE_URL + _image_link
            _image_links.append(_full_link)

        self._get_gallery(gallery_list=_image_links, _title=new_name)
        
    
    # Scrape galleries from page
    ####################################
    def scrape_galleries_from_page(self, url=None, pages=None, per_page=None):
        if pages is not None and int(pages) > 100:
            raise ValueError("'pages' parameter must not exceed 100.")
        
        print(f"Search url : {url}")
        while True:
            try:
                # checking how many pages are available
                html = requests.get(url).content
                soup = BeautifulSoup(html, 'lxml')
                max_pages = soup.find("a", "next").find_previous_sibling("a").text
                
                gallery__links = list()
                for page in range(1, (pages + 1)) if pages is not None else (range(1, 2)):
                    if page > int(max_pages):
                        print("There are only {0} pages.".format(max_pages))
                        break
                    else:
                        print("page: {0}".format(page))
                        augmented_url = url + ("page={0}".format(page) if url[-1] == "?" else "?page={0}".format(page))
                        print("link augmented: {0}".format(augmented_url))
                        html = requests.get(augmented_url).content
                        soup = BeautifulSoup(html, 'lxml')
                        galleries = soup.find_all('div', 'gallery')
                        print("Number of galleries in page: {0}".format(len(galleries)))
                        for gallery in galleries[:per_page] if per_page is not None else galleries:
                            gallery_link = gallery.find("a", "cover").get("href")
                            link = self.BASE_URL + gallery_link
                            gallery__links.append(link)
                    break
            except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError) as e:
                print("connection aborted. waiting for {0} second(s) and trying again.".format(2))
                time.sleep(3)
                continue
                        
            for g in gallery__links:
                self._scrape_images_from_page(url=g)
                
        
    def _get_gallery(self, gallery_list=None, _title=None):
        try:
            _count = 0
            for idx, link in enumerate(gallery_list):
                _direct_link = ""
                while True:
                    print("Downloading...")
                    try:   
                        html = requests.get(link).content
                        soup = BeautifulSoup(html, "lxml")
                        if soup.find('title').text == "nhentai.to | 504: Gateway time-out":
                            print("Gateway Timeout Error...Retrying.")
                            time.sleep(2)
                            continue
                        if soup.find('title').text == "nhentai.to | 520: Web server is returning an unknown error":
                            print("520: Server just hit a wall...Retrying in 2 second(s)")
                            time.sleep(2)
                            continue
                        if soup.find("img", "fit-horizontal").get('src') != None:
                            _direct_link = soup.find("img", "fit-horizontal").get('src')
                            with requests.get(_direct_link, stream=True, timeout=5) as r:
                                r.raise_for_status()
                                name = re.findall(r".+/([0-9].+.[a-z].+)", _direct_link)[0]
                                mdir = self._create_gallery_directory(dirname=_title)
                                with open(os.path.join(mdir, name), "wb") as f:
                                    for chunk in r.iter_content():
                                        if chunk:
                                            f.write(chunk)  
                        break         
                    except requests.exceptions.HTTPError:
                        print('HTTP Error. Retrying...')
                        time.sleep(2)
                        continue
                    except requests.exceptions.Timeout as TimeOutError:
                        print('Taking too long...trying again')
                        time.sleep(2)
                        continue
                    except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError) as e:
                        print("connection aborted. waiting for {0} second(s) and trying again.".format(2))
                        time.sleep(2)
                        continue
                _count += 1
                print("Downloading {0} out of {1}".format((idx + 1), len(gallery_list)))
        finally:
            print("Gallery downloaded. {0} out of {1} image(s) were saved.".format(_count, len(gallery_list)))
            print("==========================================================\n")
            time.sleep(2)