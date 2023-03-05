import functools



def check_valid_url(func):
    @functools.wraps(func)
    def url_wrapper(self=None, url=None, *args, **kwargs):
        if url is None:
            raise ValueError("URL was not provided.")
        else:
            ret = func(self, url=url)
            return ret
    return url_wrapper

