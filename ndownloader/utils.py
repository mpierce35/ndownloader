available = ["tag", "artist", "character", "parody", "group"]

def create_search_query(self, base_url=None, **kwargs):
    query = ""
    for key, value in kwargs.items():
        value = value.lower().replace(" ", "+")
        query += "{0}={1}&".format(key, value)
    
    link = base_url + query
    self.logger.info("Search URL: {0}".format(link))
    return link


def decode_title(self, tag_name):
    a = tag_name.find("a")
    res = email(tag_name.find("a")["data-cfemail"])
    self.logger.info("cfemail: -> %s" % tag_name.find("a")["data-cfemail"])
    
    tag_name.find("a").string.replace_with(res)
    return tag_name.text


def email(string):
    r = int(string[:2], 16)
    email = ''.join([chr(int(string[i:i+2], 16) ^ r) for i in range(2, len(string), 2)])
    return email


# from bs4 import BeautifulSoup

# string = """<h1>[Nerimono Koujou (Various)] Hachimiya Meguru Dosukebe Goudoushi MassachuEcchi-shuu | 八宮巡的超色合同誌 麻薩諸色州(THE <a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="f79eb3b8bbbab7a4a3b2a5">[email&#160;protected]</a>: Shiny Colors) [Chinese] [吸住没碎个人汉化] [Digital]</h1>"""

# soup = BeautifulSoup(string, "lxml")
# h1 = soup.find("h1")
# a = h1.find("a")

# print(a.has_attr("class"))

# res = email(h1.find("a")["data-cfemail"])
# print(res)
# h1.find("a").string.replace_with(res)
# print(h1.text)


test = email("e4beb1b6ada8a8ada4aab0")
print(test)