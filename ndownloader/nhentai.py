## Renaming folder names because of "email protected" needs to be changed. sometimes, there's more than one occurance and needs a loop

from BaseExtractor import BaseExtractor
import utils


class Nhentai(BaseExtractor):
    def __init__(self):
        super().__init__()
    
    
    def get_random_doujin(self):
        self._scrape_images_from_page(url=self.links['random'])
    
    
    def get_multiple_random_galleries(self, num_galleries=None):
        for _ in range(num_galleries):
            self._scrape_images_from_page(url=self.links['random'])
    
    
    def get_doujin_by_id(self, id_, zip_=False):
        search_url = self.links['gallery'] + str(id_)
        self.logger.debug("Search url {0}".format(search_url))
        self._scrape_images_from_page(url=search_url, zip_dir=zip_)


    def get_gallery_by_url(self, url):
        self._scrape_images_from_page(url=url)
        
            
    def get_doujin_by_query(self, search_query, pages=None, per_page=None):
        search_url = utils.create_search_query(self, base_url=self.links['search'], q=search_query)
        links = self.scrape_galleries_from_page(url=search_url, pages=pages, per_page=per_page)
        for l in links:
            self._scrape_images_from_page(url=l)

        
    def get_doujins_by_category(self, pages=None, per_page=None, **kwargs):
        if len(kwargs) > 1:
            raise ValueError("too many arguments were passed.")
        link = ""
        for value, key in kwargs.items():
            self.logger.info(f"{key} ==> {value}")
            if value not in utils.available:
                raise ValueError(f"the parameter '{value}' is not a category.")
            
            self.logger.info(f"Category: {value}")
            query = key.replace(" ", "-")
            link = self.links[value] + query
        links = self.scrape_galleries_from_page(url=link, pages=pages, per_page=per_page)
        for l in links:
            self._scrape_images_from_page(url=l)



x = Nhentai()
t = "396784"
# x.get_doujin_by_id(id_=t, zip_=False)
# x.get_doujins_by_category(character="meguru-hachimiya", pages=1)

