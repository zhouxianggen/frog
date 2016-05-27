
from url_cache import UrlCache
from doc_cache import DocCache

class Frog(object):
    def __init__(self):
        self.path_cache = PathCache()
        self.doc_cache = DocCache()

    def feed(self, doc):
        path = self.get_url_path(doc.url)
        urls = self.path_cache.get_urls(path)
        docs = []
        for url in urls:
            doc2 = self.doc_cache.get_doc(url)
            if doc2 and self.get_doc_similarity(doc, doc2) > 0.8:
                docs.append(doc2)
        if not docs:
            self.url_cache.add_url(path, doc.url)
            self.doc_cache.add_doc(doc)
            return

        bxps1 = self.get_base_xpaths([doc])
        bxps2 = self.get_base_xpaths(docs)
        
        sims = {}
        for k,s1 in bxps1.items():
            if k in bxps2:
                sims[k] = len(bxps2[k] & s1) / float(len(s1))
            else:
                sims[k] = 0.0

        nodes = {}
        for lev,p,t in doc.xpaths:
            if not t:
                continue
            bxp = get_base_xpath(p)
            if bxp in nodes:
                nodes[bxp][1] += t + '\n'
            else:
                ps[bp] = [sims[bp], t]
            #print '%.2f' % sims[bp], p, len(t), t[:15]




