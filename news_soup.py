
# -*- coding: utf-8 -*-

import os, sys
from collections import defaultdict
from HTMLParser import HTMLParser
import urllib2
import re
from char_util import *

class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return self.fed

class Line(object):
    def __init__(self, s):
        self.value = s.strip()
        self.char_count = 0
        self.readable_count = 0
        self.chn_count = 0
        self.punc_count = 0
        for c in self.value:
            self.char_count += 1
            t = get_char_type(c)
            if t in ['DIGIT', 'ALPHABET', 'CHN']:
                self.readable_count += 1
                if t == 'CHN':
                    self.chn_count += 1
            elif t in ['PUNC']:
                self.punc_count += 1
        self.probs = defaultdict(float)

class NewsSoup(object):
    def __init__(self):
        self.re_charset = re.compile(r'<meta\s+.*?charset\s*=\s*"?([\w-]+)"?', re.I)
        self.re_script = re.compile(r'<script\s.+?</script>', re.I|re.DOTALL)
        self.re_html_title = re.compile(r'<title>(.+?)</title>', re.I|re.DOTALL)

    def open_url(self, url, timeout=10):
        resp = urllib2.urlopen(url, timeout=timeout)
        if resp.getcode() == 200:
            return resp.read()
        return ''

    def remove_script(self, content):
        return self.re_script.sub('', content)
    
    def remove_html_tag(self, content):
        s = HTMLStripper()
        print '*******', type(content)
        s.feed(content)
        return ''.join(s.get_data())

    def get_charset(self, content):
        m = self.re_charset.search(content)
        if m:
            return m.group(1).lower()
        else:
            return 'utf8'

    def get_html_title(self, content):
        m = self.re_html_title.search(content)
        if m:
            return m.group(1).replace('\n', '').strip()
        return ''
    
    def find_titles(self, lines):
        phrases = set(split_by_phrase(self.html_title))
        for line in lines:
            if line.chn_count < 6 or line.punc_count > 0:
                continue
            if float(line.readable_count) / line.char_count < 0.7:
                continue
            if float(line.chn_count) / line.readable_count < 0.7:
                continue
            total, hit = 0, 0
            for p in split_by_phrase(line.value):
                total += len(p)
                if p in phrases:
                    hit += len(p)
            line.probs['title'] = float(hit) / total
       
    def find_sentences(self, lines):
        for line in lines:
            if line.punc_count > 0 and line.chn_count > 6:
                line.probs['sentence'] = 1.0
        i, s = 0, len(lines)
        while i < s:
            if lines[i].probs['sentence'] > 0.8:
                j = i + 1
                while j < s:
                    if lines[j].probs['sentence'] > 0.8:
                        lines[i].value += '\n' + lines[j].value
                        lines[i].char_count += lines[j].char_count
                        lines[i].readable_count += lines[j].readable_count
                        lines[i].chn_count += lines[j].chn_count
                        lines[i].punc_count += lines[j].punc_count
                        j += 1
                    else:
                        break
                for x in range(i+1, j):
                    lines.pop(i+1)
            i, s = i+1, len(lines)
    
    def parse_from_url(self, url):
        content = self.open_url(url)
        open('content1', 'wb').write(content)
        self.charset = self.get_charset(content)
        print self.charset
        self.html_title = self.get_html_title(content)
        self.html_title = self.html_title.decode(self.charset)

        content = self.remove_script(content)
        content = self.remove_html_tag(content)
        open('content2', 'wb').write(content)
        content = content.decode(self.charset)
        
        lines = [Line(x.strip()) for x in content.split('\n') if x.strip()]
        self.find_titles(lines)
        self.find_sentences(lines)
        
        title, body = '', ''
        for ln in lines:
            if ln.probs['title'] > 0.8 and len(ln.value) > len(title):
                title = ln.value
            if ln.probs['sentence'] > 0.8 and len(ln.value) > len(body):
                body = ln.value
            print '\n', ln.value
            print ln.char_count, ln.readable_count, ln.chn_count, ln.punc_count
            print '   prob_title:', ln.probs['title']
            print 'prob_sentence:', ln.probs['sentence']

        print '>>>>>>>>>>>>>>>>>>>>>>'
        print title
        print body

ns = NewsSoup()
#ns.parse_from_url('http://hunan.voc.com.cn/xhn/article/201605/201605040700175133.html')
#ns.parse_from_url('http://www.hn.xinhuanet.com/2016-05/03/c_1118794294.htm')
ns.parse_from_url(sys.argv[1])

