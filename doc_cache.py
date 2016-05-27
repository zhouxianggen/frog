
from collections import defaultdict

class DocCache(object):
    map = {}

    def add_doc(self, doc):
        self.map[doc.url] = doc
            
    def get_doc(self, url):
        if url in self.map:
            return self.map[url]
        return None

