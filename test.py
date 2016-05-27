
import os, sys
import re
from collections import defaultdict
from doc import Doc
import codecs


re_base = re.compile(r'\[\d+\]$')
def get_base_path(path):
    return re_base.sub('', path)

def get_text_similarity(t1, t2):
    if t1 == t2:
        return 1.0
    return 0.0

def get_bps(docs):
    bps = defaultdict(set)
    for doc in docs:
        for lev, p, t in doc.xpaths:
            if t:
                bps[get_base_path(p)].add(t)
    return bps

urls = []
urls.append('http://news.163.com/16/0525/01/BNSGE6RD00014Q4P.html')
urls.append('http://news.163.com/16/0525/02/BNSM85IC00011229.html')
urls.append('http://news.163.com/16/0525/13/BNTR1M3R00011229.html')
urls.append('http://news.163.com/16/0525/01/BNSGF9F100014AED.html')

#urls.append('http://www.zgxcfx.com/zhubiantuijian/85839.html')
#urls.append('http://www.zgxcfx.com/zhubiantuijian/85030.html')
#urls.append('http://www.zgxcfx.com/zhubiantuijian/85022.html')

docs = [Doc(url) for url in urls]

bps1 = get_bps(docs[:1])
bps2 = get_bps(docs[1:])

sims = {}
for k,s1 in bps1.items():
    if k in bps2:
        sims[k] = len(bps2[k] & s1) / float(len(s1))
    else:
        sims[k] = 0.0

ps = {}
for lev,p,t in docs[0].xpaths:
    if not t:
        continue
    bp = get_base_path(p)
    if bp in ps:
        ps[bp][1] += t + '\n'
    else:
        ps[bp] = [sims[bp], t]
    #print '%.2f' % sims[bp], p, len(t), t[:15]

for k,v in ps.items():
    print k, v[0], len(v[1])
sys.exit()

sames = {}
paths = {x[1]:[x[2], 0] for x in docs[0].xpaths}

for d in docs[1:]:
    for lev,p,t in d.xpaths:
        if p in paths:
            paths[p][1] += get_text_similarity(paths[p][0], t)

for lev,p,t in docs[0].xpaths:
    print '%.2f' % paths[p][1], p, len(t), t[:15]

sys.exit()

for i,url in enumerate(urls):
    d = Doc(url)
    wlns = [x[2].strip() for x in d.xpaths if x[2].strip()]
    codecs.open('doc_%d' % i, 'wb', 'utf8').writelines(wlns)
sys.exit()


doc1 = Doc('http://ts.voc.com.cn/question/view/338003.html')
doc2 = Doc('http://ts.voc.com.cn/question/view/338012.html')

s1 = {x[1]:x[2] for x in doc1.xpaths}
s2 = {x[1]:x[2] for x in doc2.xpaths}

ts1 = []
for lev,path,text in doc1.xpaths:
    if path in s2 and s2[path] == text:
        continue
    if text:
        ts1.append(text)
codecs.open('doc1', 'wb', 'utf8').write('\n'.join(ts1))

ts2 = []
for lev,path,text in doc2.xpaths:
    if path in s1 and s1[path] == text:
        continue
    if text:
        ts2.append(text)
codecs.open('doc2', 'wb', 'utf8').write('\n'.join(ts2))
sys.exit()

s1 = {x[1]:x[0] for x in doc1.xpaths}
s2 = {x[1]:x[0] for x in doc2.xpaths}

diffs = defaultdict(int)
for k,v in s1.items():
    if k not in s2:
        diffs[v] += 1
for k,v in s2.items():
    if k not in s1:
        diffs[v] += 1
print diffs
m = min(diffs.keys())
print m

a1 = []
s, e = 0, len(doc1.xpaths)
while s < e:
    print doc1.xpaths[s][1]
    if doc1.xpaths[s][0]+1 == m:
        texts = [doc1.xpaths[s][2]]
        j = s + 1
        while j < e and doc1.xpaths[j][0] >= m:
            texts.append(doc1.xpaths[j][2])
            j += 1
        a1.append(' + '.join(texts))
        s = j
    else:
        a1.append(doc1.xpaths[s][2])
        s += 1

a2 = []
s, e = 0, len(doc2.xpaths)
while s < e:
    if doc2.xpaths[s][0]+1 == m:
        texts = [doc2.xpaths[s][2]]
        j = s + 1
        while j < e and doc2.xpaths[j][0] >= m:
            texts.append(doc2.xpaths[j][2])
            j += 1
        a2.append(' + '.join(texts))
        s = j
    else:
        a2.append(doc2.xpaths[s][2])
        s += 1

print len(a1), len(a2)

for t1,t2 in zip(a1, a2):
    print 'START\n%s\n\t****\n%s\nEND' % (t1, t2)

open('doc1', 'wb').write('\n'.join([x[1] for x in doc1.xpaths if x[0] <= 5]))
open('doc2', 'wb').write('\n'.join([x[1] for x in doc2.xpaths if x[0] <= 5]))

sys.exit()

for p,t in doc1.xpaths:
    print p
print len(doc1.xpaths)
print len(set([x[0] for x in doc1.xpaths]))

doc2 = Doc('http://ts.voc.com.cn/question/view/338012.html')
open('doc2', 'wb').write('\n'.join([x[0] for x in doc2.xpaths]))

print doc1.simhash
print doc2.simhash
