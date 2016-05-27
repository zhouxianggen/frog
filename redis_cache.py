
import redis

class UrlCache(object):
    def __init__(self, host='localhost', port=6377):
        self.r = redis.StrictRedis(host, port, db=0)

    def add_url(self, path, url):
        self.r.sadd(path, url)

    def get_urls(self, path):
        return self.r.smembers(path)

uc = UrlCache()
uc.add_url('path1', 'jim')
uc.add_url('path1', 'cate')
print uc.get_urls('path1')
