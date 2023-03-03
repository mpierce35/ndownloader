from bs4 import BeautifulSoup
import concurrent.futures
import requests
import urllib3
import re
import os
import time
import ctypes
from fake_useragent import UserAgent
import shutil
import logging

from decorators import check_valid_url
from utils import decode_title

class BaseExtractor(object):
    def __init__(self, dirname=None):
        self.loggerConfig = logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(asctime)s - %(filename)s/%(funcName)s --> %(message)s")
        self.logger = logging.getLogger(__name__)
        self.BASE_DIR = dirname if dirname is not None else self._create_init_directory()
        self.GALLERY_DIR_NAME = ""
        self.headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "Connection" : "Keep-Alive"
        }
        self.links = {
            "base" : "https://nhentai.to",
            "artist" : "https://nhentai.to/artist/",
            "tag": "https://nhentai.to/tag/",
            "character" : "https://nhentai.to/character/",
            "parody": "https://nhentai.to/parody/",
            "group": "https://nhentai.to/group/",
            "random" : "https://nhentai.to/random/",
            "gallery": "https://nhentai.to/g/",
            "search" : "https://nhentai.to/search?", 
            "direct_link" : "https://t.dogehls.xyz/galleries/",
        }

    @property
    def GALLERY_DIR_NAME(self):
        return self._GALLERY_DIR_NAME
        
        
    @GALLERY_DIR_NAME.setter
    def GALLERY_DIR_NAME(self, value):
        self._GALLERY_DIR_NAME = value

    #create parent directory if not found
    def _create_init_directory(self) -> str:
        default_dir = os.path.join(os.path.dirname(__file__), 'automated')
        if os.path.exists(default_dir) == False:
            os.mkdir(default_dir)
            self.logger.info("Default directory created.")
        else:
            self.logger.info("Default directory exists.")
        return default_dir
        
    
    #create directory for the specified gallery    
    def _create_gallery_directory(self, dirname=None) -> str:
        # to avoid moving/copying directories by user, I'm limiting folder's name to 255 characters
        newdir = os.path.join(self.BASE_DIR, dirname)
        if os.path.exists(newdir) == False:
            os.mkdir(newdir)
            self.logger.info("Gallery directory was created.")
        return newdir
    
    
    #comeback later.
    def _create_temp_directory(self):
        path = os.path.join(self.BASE_DIR, "_temp")
        if os.path.exists(path) == False:
            os.mkdir(path)
            ctypes.windll.kernel32.SetFileAttributesW(path, 2)
            print("Temporary directory created.")
        else:
            print("Temporary directory already exists.")
        return path
    
    
    #converts directory to a zip file
    def _convert_directory_to_zip(self, path):
        try:
            directory_name = os.path.basename(path)[:255]
            clean_path = os.path.join(self.BASE_DIR, directory_name)
            os.remove(os.path.join(clean_path, "Thumbs.db"))
            shutil.make_archive(clean_path, "zip", os.path.join(self.BASE_DIR, self.GALLERY_DIR_NAME))
        finally:
            shutil.rmtree(clean_path)



    ###########################################
    # Scrape images from one gallery
    ###########################################   
    def _scrape_images_from_page(self, url:str, zip_dir:bool=False) -> None:
        _image_links = list()
        invalid_chars = f'<>:"\/|?*.@'
        pattern = r'[' + invalid_chars + ']'
        html = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(html.content, 'lxml')        
        _id = re.findall(r"/([0-9].+)", html.url)[0]            
        title = soup.find("h1")
        containers = soup.find_all("div", "thumb-container")
        
        if(title.find("a") and title.find("a").has_attr("data-cfemail")):
            # somewhere in the title, a special character resides. titles like ID@LMASTER usually makes an error while creating a directory.
            self.logger.info("Email tag protected by CloudFlare detected.")
            decode_title(self, tag_name=title)
        else:
            self.logger.info("No email protected tags were found")

        x = re.sub(pattern, ' ', title.text)
        
        self.logger.info("Title: {0}".format(title.text))
        self.logger.info("ID: {0}".format(_id))
        self.logger.info("Number of images: {0}".format(len(containers)))
        self.GALLERY_DIR_NAME = f"{_id}-{x}"[:200]
        self._create_gallery_directory(dirname=self.GALLERY_DIR_NAME)
            
        for image in containers:
            _image_link = image.find("a", "gallerythumb").get('href')
            _full_link = self.links['base'] + _image_link
            _image_links.append(_full_link)
            
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.get_file, _image_links)
            
        if zip_dir == True:
            self._convert_directory_to_zip(path=self.GALLERY_DIR_NAME)
            
            
    ####################################
    # Scrape galleries from page
    ####################################
    def scrape_galleries_from_page(self, url:str=None, pages:int=None, per_page:int=None) -> list:
        
        # if pages is not None and int(pages) > 100:
        #     raise ValueError("'pages' parameter must not exceed 100.") 
        while True:
            try:
                try:
                    html = requests.get(url).content
                    soup = BeautifulSoup(html, 'lxml')
                    max_pages = soup.find("a", "next").find_previous_sibling("a").text
                    self.logger.debug("Number of pages: %i" % int(max_pages))
                except AttributeError:
                    max_pages = 1
                    
                gallery__links = list()
                for page in range(1, (pages + 1)) if pages is not None else (range(1, 2)):
                    if page > int(max_pages):
                        break
                    else:
                        augmented_url = url + ("page={0}".format(page) if url[-1] == "?" else "?page={0}".format(page))
                        html = requests.get(augmented_url).content
                        soup = BeautifulSoup(html, 'lxml')
                        galleries = soup.find_all('div', 'gallery')

                        self.logger.info("scraping page: {0}".format(page))
                        self.logger.info("Augmented link: {0}".format(augmented_url))
                        self.logger.info("Number of galleries in page: {0}".format(len(galleries)))
                                                
                        for gallery in galleries[:per_page] if per_page is not None else galleries:
                            gallery_link = gallery.find("a", "cover").get("href")
                            link = self.links['base'] + gallery_link
                            gallery__links.append(link)
                        break 
                          
            except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError) as e:
                print("Connection aborted. Waiting for {0} second(s) and trying again.".format(3))
                time.sleep(3)
                continue
            
            return gallery__links


    #downloads a single link and save file
    # change it to show donwload progress
    def get_file(self, link, num_retries:int=20, gallery_path:str=None):
        i = 0
        while True:
            self.logger.info("Downloading file...\n")
            try:   
                if i >= num_retries : return self.logger.error("Error while downloading file.")
                html = requests.get(link).content
                soup = BeautifulSoup(html, "lxml")
                if soup.find('title').text == "nhentai.to | 504: Gateway time-out":
                    print("Gateway Timeout Error...Retrying.")
                    time.sleep(2)
                    i += 1
                    continue
                if soup.find('title').text == "nhentai.to | 520: Web server is returning an unknown error":
                    print("520: Server just hit a wall...Retrying in 2 second(s)")
                    time.sleep(2)
                    i += 1
                    continue
                if soup.find("img", "fit-horizontal").get('src') != None:
                    _direct_link = soup.find("img", "fit-horizontal").get('src')
                    with requests.get(_direct_link, stream=True, timeout=5, headers=self.headers) as r:
                        r.raise_for_status()
                        _name = re.findall(r".+/([0-9].+.[a-z].+)", _direct_link)[0]
                        x = os.path.join(self.BASE_DIR, self.GALLERY_DIR_NAME)
                        with open(gallery_path if gallery_path is not None else os.path.join(x, _name), "wb") as f:
                            for chunk in r.iter_content():
                                if chunk:
                                    f.write(chunk)                 
                break
                        
            except requests.exceptions.Timeout:
                print('Taking too long...trying again')
                time.sleep(2)
                continue
            except (requests.exceptions.ConnectionError, urllib3.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
                print("connection aborted. waiting for {0} second(s) and trying again.".format(2))
                time.sleep(2)
                continue
        