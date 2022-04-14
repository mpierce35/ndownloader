from BaseExtractor import BaseExtractor
import utils
import concurrent.futures

class Nhentai(BaseExtractor):
    def __init__(self):
        super().__init__()
    
    
    def get_random_doujin(self):
        self._scrape_images_from_page(url=self.links['random'])
    
    def get_multiple_random_gallery(self, galleries=None):
        for _ in range(galleries):
            self._scrape_images_from_page(url=self.links['random'])
    
    def get_doujin_by_id(self, id_):
        search_url = self.links['gallery'] + str(id_)
        self._scrape_images_from_page(url=search_url)


    def get_gallery_by_url(self, url):
        self._scrape_images_from_page(url=url)
        
            
    def get_doujin_by_query(self, search_query, pages=None, per_page=None):
        search_url = utils.create_search_query(base_url=self.links['search'], q=search_query)
        links = self.scrape_galleries_from_page(url=search_url, pages=pages, per_page=per_page)
        
        for l in links:
            self._scrape_images_from_page(url=l)

        
    def get_doujins_by_category(self, pages=None, per_page=None, **kwargs):
        if len(kwargs) > 1:
            raise ValueError("too many arguments were passed.")
        
        link = ""
        for value, key in kwargs.items():
            print(f"value: {value} / key : {key}")
            if value not in utils.available:
                raise ValueError(f"the parameter '{value}' is not a category.")
            
            print(f"Category: {value}")    
            query = key.replace(" ", "-")
            link = self.links[value] + query
        links = self.scrape_galleries_from_page(url=link, pages=pages, per_page=per_page)
        for l in links:
            self._scrape_images_from_page(url=l)

