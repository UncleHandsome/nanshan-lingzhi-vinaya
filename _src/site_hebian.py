# -*- coding: utf-8 -*-
"""句級合編 → docs/hebian/*.html（側欄改用與 site2 相同的書目列表）"""
import io, os, re, glob
from docx import Document
from docx.oxml.ns import qn

D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(D, 'docs')
OUT = os.path.join(SITE, 'hebian')
os.makedirs(OUT, exist_ok=True)

BOOKS = [
    ('xingshichao', '四分律刪繁補闕行事鈔'),
    ('jieshu', '四分律含注戒本疏'),
    ('yeshu', '四分律刪補隨機羯磨疏'),
    ('zhichi', '四分律行事鈔資持記'),
    ('nicao', '四分比丘尼鈔'),
    ('yichao', '四分律拾毗尼義鈔'),
]


def nav(cur_vol=None):
    parts = ['<nav><h1><a href="../index.html">南山律典・白話對照</a></h1>']
    parts.append('<div class="grp"><b>全書</b><a href="../index.html">目錄</a>'
                 '<a href="../search.html">全文搜尋</a><a href="../appendix.html">附錄</a></div>')
    parts.append('<div class="grp"><b>分卷</b><div class="bklist">')
    for out, title in BOOKS:
        vols = [os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(SITE, out, '*.html')))]
        if not vols:
            continue
        parts.append('<details class="navj"><summary>' + title + '</summary><ul>')
        for v in vols:
            parts.append('<li><a href="../%s/%s.html">%s</a></li>' % (out, v, v))
        parts.append('</ul></details>')
    parts.append('<details class="navj" open><summary class="cur">行事鈔資持記・句級合編</summary><ul>')
    for v in ('卷上之一','卷上之二','卷上之三','卷上之四','卷中之一','卷中之二','卷中之三','卷中之四','卷下之一','卷下之二','卷下之三','卷下之四'):
        parts.append('<li><a href="%s.html">%s</a></li>' % (v, v))
    parts.append('</ul></details>')
    parts.append('</div></div></nav>')
    return ''.join(parts)


TPL = '''<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title>
<link rel="stylesheet" href="../style.css?v=4"></head><body><div class="wrap">
%s<main><h1>%s</h1><div class="intro">鈔文與記文逐段並列：淺褐為鈔、淺藍為記；每段附白話。</div>
%s
</main></div></body></html>'''


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')


def shaded(p):
    return p._p.find('.//' + qn('w:shd')) is not None


for vol in ('卷上之一','卷上之二','卷上之三','卷上之四','卷中之一','卷中之二','卷中之三','卷中之四','卷下之一','卷下之二','卷下之三','卷下之四'):
    src = os.path.join(D, '白話', '行事鈔資持記句級合編_%s.docx' % vol)
    if not os.path.exists(src):
        continue
    d = Document(src)
    body = []
    prev = None
    for p in d.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if p.style.name.startswith('Heading'):
            body.append('<h2>%s</h2>' % esc(t))
            prev = None
            continue
        if shaded(p):
            cls = 'src' if not t.startswith('【記') else 'src2'
            body.append('<div class="%s">%s</div>' % (cls, esc(t)))
            prev = 'src'
            continue
        if prev in ('src', 'tr'):
            body.append('<div class="tr">%s</div>' % esc(t))
            prev = 'tr'
    html = TPL % ('句級合編 ' + vol, nav(vol), '四分律行事鈔資持記　句級合編（' + vol + '）', '\n'.join(body))
    io.open(os.path.join(OUT, vol + '.html'), 'w', encoding='utf-8').write(html)
    print(vol, len(body))
