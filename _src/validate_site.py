# -*- coding: utf-8 -*-
"""網站驗收：導覽錨點必須存在，長原文必須有句讀。"""
import io, json, os, re, sys
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {'xingshichao': ['卷上','卷中','卷下'], 'yeshu': ['卷一','卷二','卷三','卷四'], 'nicao': ['卷上','卷中','卷下'], 'yichao': ['卷上','卷中']}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', s))
nav = json.load(io.open(os.path.join(B,'docs','nav.json'), encoding='utf-8'))
navmap = {b['out']: b for b in nav['books']}
bad = []
for book, vols in BOOKS.items():
    for v in vols:
        p = os.path.join(B,'docs',book,v+'.html')
        t = io.open(p, encoding='utf-8').read()
        ids = set(re.findall(r'id="([^"]+)"', t))
        for sec in navmap.get(book,{}).get('vols',[]):
            if sec['v'] == v:
                for sid, label in sec['secs']:
                    if sid not in ids:
                        bad.append(('ANCHOR', book, v, sid, label))
        for m in re.finditer(r'<div class="o[^"]*">(.*?)</div>', t, re.S):
            x = re.sub('<[^>]+>', '', m.group(1)); n = len(han(x)); punct = len(re.findall(r'[，。；：！？、]', x))
            if n > 30 and punct / n < 0.01:
                bad.append(('PUNCT', book, v, x[:50]))
for b in bad[:20]: print(b)
print('issues', len(bad))
sys.exit(1 if bad else 0)
