# -*- coding: utf-8 -*-
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

re_split_by_phrase = re.compile(ur'[^\u4E00-\u9FA50-9a-zA-Z]+')
def split_by_phrase(s):
    return re_split_by_phrase.sub(' ', s.lower()).split()

