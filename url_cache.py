
from collections import defaultdict

class UrlCache(object):
    PATH_SIZE = 5
    map = defaultdict(list)

    def add_url(self, path, url):
        lst = self.map[path]
        if url not in lst:
            lst.append(url)
            if len(lst) > self.PATH_SIZE:
                lst.pop(0)
            
    def get_urls(self, path):
        return self.map[path]

