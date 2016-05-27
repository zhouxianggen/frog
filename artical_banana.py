
# -*- coding: utf-8 -*-

import os, sys
import codecs
from HTMLParser import HTMLParser
import urllib2
import re

def isdigit(u):
    if u>=0x30 and u<=0x39:
        return True
    return False

def isalphabet(u):
    if (u>=0x41 and u<=0x5A) or (u>=0x61 and u<=0x7A):
        return True
    return False

def ischn(u):
    if u>=0x4E00 and u<=0x9FA5:
        return True
    return False

def ispunc(u):
    # 。，？！；
    if u in [0x3002, 0xFF0C, 0xFF1F, 0xFF01, 0xFF1B]:
        return True
    return False

def get_char_type (c):
    u = ord(c)
    if isdigit(u): return 'DIGIT'
    if isalphabet(u): return 'ALPHABET'
    if ischn(u): return 'CHN'
    if ispunc(u): return 'PUNC'
    return 'NONE'

re_phrase = re.compile(ur'[^\u4E00-\u9FA50-9a-zA-Z]+')
def phrase_split(s):
    return re_phrase.sub(' ', s.lower()).split()

class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return self.fed

class Line(object):
    text = ''
    char_count = 0
    readable_char_count = 0
    chn_char_count = 0
    punc_char_count = 0
    end_with_punc = False
    prob_title = 0.0
    prob_sentence = 0.0
    prob_source = 0.0
    prob_date = 0.0

    def __init__(self, s):
        self.text = s.strip()
        for idx,c in enumerate(self.text):
            self.char_count += 1
            t = get_char_type(c)
            if t in ['DIGIT', 'ALPHABET', 'CHN']:
                self.readable_char_count += 1
                if t == 'CHN':
                    self.chn_char_count += 1
            elif t in ['PUNC']:
                self.punc_char_count += 1
        if self.text and get_char_type(self.text[-1]) == 'PUNC':
            self.end_with_punc = True

    def __str__(self):
        return '[chars](all=%3d, readable=%3d, chn=%3d, punc=%3d, ewp=%d) [probs](title=%.2f, sentence=%.2f)' % (self.char_count, self.readable_char_count, self.chn_char_count, self.punc_char_count, self.end_with_punc, self.prob_title, self.prob_sentence)

class Block(object):
    type = 0
    start = 0
    end = 0
    text = ''
    readable_char_count = 0

    def __init__(self, lines, i, j, type):
        self.start = i
        self.end = j
        self.type = type
        counts = [x.readable_char_count for x in lines[i:j]]
        self.readable_char_count = sum(counts)
        self.text = '\n'.join([x.text for x in lines[i:j]])

    def __str__(self):
        return '[block](type=%3d, start=%3d, end=%3d, len=%4d)' % (self.type, self.start, self.end, self.readable_char_count)

    def score(self):
        return self.readable_char_count

class ArticalBanana(object):
    re_charset = re.compile(r'<meta\s+.*?charset\s*=\s*"?([\w-]+)"?', re.I)
    re_script = re.compile(r'<script.+?</script>', re.I|re.DOTALL)
    re_style = re.compile(r'<style.+?</style>', re.I|re.DOTALL)
    re_head = re.compile(r'<head.+?</head>', re.I|re.DOTALL)
    re_html_title = re.compile(r'<title>(.+?)</title>', re.I|re.DOTALL)

    url = ''
    status_code = 0
    content = ''
    encoding = 'utf8'
    html_title = ''
    text = ''
    lines = []
    blocks = []
    title = ''
    body = ''

    def __init__(self, url):
        self.url = url

    def download(self):
        resp = urllib2.urlopen(self.url, timeout=10)
        self.status_code = resp.getcode()
        if self.status_code == 200:
            self.content = resp.read()
        open('content', 'wb').write(self.content)

    def parse(self):
        self.get_encoding()
        self.get_html_title()
        #print 'encoding: ', self.encoding
        self.get_text()
        codecs.open('text', 'wb', 'utf8').write(self.text)
        self.get_lines()
        self.find_titles()
        self.find_sentences()
        self.find_blocks()

        title_score = 0.4
        for ln in self.lines:
            print ln
            if ln.prob_title >= title_score and len(ln.text) > len(self.title):
                title_score = ln.prob_title
                self.title = ln.text
        body_score = 30
        for b in self.blocks:
            print b
            if b.score() > body_score:
                body_score = b.score()
                self.body = b.text
    
    def remove_html_tag(self, content):
        s = HTMLStripper()
        s.feed(content)
        return ''.join(s.get_data())

    def get_encoding(self):
        m = self.re_charset.search(self.content)
        if m:
            self.encoding = m.group(1).lower().strip()
        if self.encoding == 'gb2312':
            self.encoding = 'gbk'

    def get_html_title(self):
        m = self.re_html_title.search(self.content)
        if m:
            self.html_title = m.group(1).replace('\n', '').strip()
            self.html_title = self.html_title.decode(self.encoding)
    
    def get_text(self):
        text = self.content
        text = text.replace('</div>', '</div>\n')
        text = text.replace('</p>', '</p>\n')
        text = self.re_style.sub('', text)
        text = self.re_script.sub('', text)
        text = self.re_head.sub('', text)
        text = text.decode(self.encoding)
        self.text = self.remove_html_tag(text)

    def get_lines(self):
        self.lines = [Line(x.strip()) for x in self.text.split('\n') if x.strip()]

    def find_titles(self):
        phrases = set(phrase_split(self.html_title))
        for line in self.lines:
            if line.chn_char_count < 6:
                continue
            if float(line.readable_char_count) / line.char_count < 0.7:
                continue
            if float(line.chn_char_count) / line.readable_char_count < 0.7:
                continue
            total, hit = 0, 0
            for p in phrase_split(line.text):
                total += len(p)
                if p in phrases:
                    hit += len(p)
            line.prob_title = float(hit) / total
       
    def find_sentences(self):
        for line in self.lines:
            if line.readable_char_count >= 4 and line.end_with_punc:
                line.prob_sentence = 1.0
            if line.punc_char_count > 1 and line.chn_char_count >= 4:
                line.prob_sentence = 1.0
            line.prob_sentence -= line.prob_title

    def find_blocks(self):
        i, s = 0, len(self.lines)
        while i < s:
            if self.lines[i].prob_sentence > 0.8:
                j = i + 1
                while j < s and self.lines[j].prob_sentence > 0.8:
                    j += 1
                self.blocks.append(Block(self.lines, i, j, 1))
                i = j
            else:
                self.blocks.append(Block(self.lines, i, i+1, 0))
                i += 1
       
a = ArticalBanana(sys.argv[1])
a.download()
a.parse()

print '<TITLE>'
print a.title
print '<BODY>'
print a.body

