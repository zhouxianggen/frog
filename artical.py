# -*- coding: utf-8 -*-

import sys
import urllib2
from lxml.html.clean import Cleaner
from lxml import html

class Artical(object):
    url = ''
    status_code = 0
    content = ''
    
    def __init__(self, url):
        self.url = url
        self.cleaner = Cleaner()
        self.cleaner.scripts = True
        self.cleaner.javascript = True
        self.cleaner.comments = True
        self.cleaner.style = True
        self.cleaner.remove_tags = ['b', 'big', 'i', 'small', 'tt', 'abbr', 'acronym', 'cite', 'code', 'dfn', 'em', 'kbd', 'strong', 'samp', 'time', 'var', 'a', 'bdo', 'br', 'img', 'map', 'object', 'q', 'script', 'span', 'sub', 'sup', 'button', 'input', 'label', 'select', 'textarea']

    def download(self, url):
        resp = urllib2.urlopen(url, timeout=10)
        self.status_code = resp.getcode()
        if self.status_code == 200:
            self.content = resp.read()
        open('content', 'wb').write(self.content)
        return self.content

    def get_xnodes(self, t, r):
        yield (r.getpath(t), t.text)
        for c in t.getchildren():
            for x in self.get_xnodes(c, r):
                yield x

    def pretreat(self):
        #c1 = self.download('http://ts.voc.com.cn/note/view/32985.html')
        c1 = self.download('http://ts.voc.com.cn/question/view/338003.html')
        t1 = self.cleaner.clean_html(html.fromstring(c1))
        r1 = t1.getroottree()
        nodes1 = [x for x in self.get_xnodes(t1, r1)]
        open('t1', 'wb').writelines(['%s\n' % (x[0]) for x in nodes1])
        
        c2 = self.download('http://ts.voc.com.cn/question/view/338012.html')
        t2 = self.cleaner.clean_html(html.fromstring(c2))
        r2 = t2.getroottree()
        nodes2 = [x for x in self.get_xnodes(t2, r2)]
        open('t2', 'wb').writelines(['%s\n' % (x[0]) for x in nodes2])

        diffs = []
        d1 = {x[0]:x[1].strip() if x[1] else '' for x in nodes1}
        for p,t in nodes2:
            t = t.strip() if t else ''
            if p in d1:
                diffs.append((abs(len(d1[p])-len(t)), t, d1[p]))
            else:
                diffs.append((-1, t, ''))
        for x in diffs:
            print x[0], x[1], ' ++++ ', x[2]

        s1 = set([x[0] for x in nodes1])
        s2 = set([x[0] for x in nodes2])
        c = s1 & s2
        print len(s1), len(s2), len(c)
        

    def parse(self):
        self.pretreat()
       
a = Artical(sys.argv[1])
a.parse()

