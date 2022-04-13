from BaseExtractor import BaseExtractor
from utils import Helpers

class Nhentai(BaseExtractor):
    def __init__(self):
        super().__init__()
    
    
    def get_random_doujin(self):
        self._scrape_images_from_page(url=self.links['random'])
        
    
    def get_doujin_by_id(self, id_=None):
        search_url = self.links['gallery'] + str(id_)
        self._scrape_images_from_page(url=search_url)
        
        
    def get_doujin_by_query(self, search_query=None, pages=None, per_page=None):
        if search_query is None:
            raise ValueError("'search_query' parameter is required. Or else, what am I supposed to search for?")
        search_url = Helpers().create_search_query(base_url=self.links['search'], q=search_query)
        self.scrape_galleries_from_page(url=search_url, pages=pages, per_page=per_page)

        
    def get_doujins_by_category(self, pages=None, per_page=None, **kwargs):
        available = ["tag", "artist", "character", "parody", "group"]
        if len(kwargs) > 1:
            raise ValueError("too many arguments were passed.")
        link = str()
        for value, key in kwargs.items():
            print(f"value: {value} / key : {key}")
            if value not in available:
                raise ValueError(f"the parameter '{value}' is not a category.")
            print(f"Category: {value}")    
            query = key.replace(" ", "-")
            link = self.categories[value] + query
        self.scrape_galleries_from_page(url=link, pages=pages, per_page=per_page)

debug = Nhentai()
debug.get_doujin_by_query(search_query="mythra", pages=1)
