import functools



def check_valid_url(func):
    @functools.wraps(func)
    def url_wrapper(self, url=None, *args, **kwargs):
        if url is None:
            raise ValueError("URL was not provided.")
    return url_wrapper
         
         
