from BaseExtractor import BaseExtractor
from utils import Helpers

class Nhentai(BaseExtractor):
    def __init__(self):
        super().__init__()
    
    
    def get_random_doujin(self):
        self._scrape_images_from_page(url=self.RANDOM_URL)
        
    
    def get_doujin_by_id(self, id_=None):
        search_url = self.GALLERY_URL + str(id_)
        self._scrape_images_from_page(url=search_url)
        
        
    def get_doujin_by_query(self, search_query=None, pages=None, per_page=None):
        if search_query is None:
            raise ValueError("'search_query' parameter is required. Or else, what am I supposed to search for?")
        
        search_url = Helpers().create_search_query(base_url=self.SEARCH_URL, q=search_query)
        self.scrape_galleries_from_page(url=search_url, pages=pages, per_page=per_page)
        
        
        
        
        
        
debug = Nhentai()
# debug.get_doujin_by_id(id_=386602)
debug.get_doujin_by_query(search_query="Jeanne D'Arc", pages=2, per_page=10)
