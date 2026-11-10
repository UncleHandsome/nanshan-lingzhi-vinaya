# -*- coding: utf-8 -*-
"""句級合編 → docs/hebian/*.html（三層側欄：書 → 卷 → 篇）"""
import io, os, re, glob, html, json
from docx import Document

import site_assets as SA

D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(D, 'docs')
OUT = os.path.join(SITE, 'hebian')
os.makedirs(OUT, exist_ok=True)

HB = ['卷上之一', '卷上之二', '卷上之三', '卷上之四', '卷中之一', '卷中之二', '卷中之三', '卷中之四',
      '卷下之一', '卷下之二', '卷下之三', '卷下之四']
BOOKS = [
    ('xingshichao', '四分律刪繁補闕行事鈔'),
    ('jieshu', '四分律含注戒本疏'),
    ('yeshu', '四分律刪補隨機羯磨疏'),
    ('zhichi', '四分律行事鈔資持記'),
    ('nicao', '四分比丘尼鈔'),
    ('yichao', '四分律拾毗尼義鈔'),
]
VOL_ORDER = ['卷上之一', '卷上之二', '卷上之三', '卷上之四',
             '卷中之一', '卷中之二', '卷中之三', '卷中之四',
             '卷下之一', '卷下之二', '卷下之三', '卷下之四',
             '卷上', '卷中', '卷下', '卷一', '卷二', '卷三', '卷四',
             '上一上', '上一下', '上二', '上三', '上四',
             '中一上', '中一下', '中二', '中三上', '中三下', '中四上', '中四下',
             '下一', '下二', '下三', '下四']


def vkey(v):
    try:
        return VOL_ORDER.index(v)
    except ValueError:
        return 999


SEC = re.compile(r'^第(\d+)篇　(.+?)(（續）)?$')


def book_toc(out):
    t = {}
    for f in glob.glob(os.path.join(SITE, out, '*.html')):
        v = os.path.basename(f)[:-5]
        h = io.open(f, encoding='utf-8').read()
        pat = re.compile(r'<a href="[^"]*' + re.escape(out) + '/' + re.escape(v) + r'\.html#p(\d+)">([^<]+)</a>')
        items, seen = [], set()
        for m in pat.finditer(h):
            sid = int(m.group(1))
            if sid in seen:
                continue
            seen.add(sid)
            items.append((sid, m.group(2)))
        t[v] = items
    return t


ENTRIES = []
for vi, vol in enumerate(HB):
    src = os.path.join(D, '白話', '行事鈔資持記句級合編_%s.docx' % vol)
    if not os.path.exists(src):
        continue
    d = Document(src)
    body, toc = [], []
    pending = None
    for p in d.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        m = SEC.match(t)
        if m:
            sid = len(toc) + 1
            toc.append((sid, t))
            body.append('<h2 class="sec" id="p%d">%s</h2>' % (sid, html.escape(t)))
            pending = None
            continue
        if t.startswith('【鈔】') or t.startswith('【記】'):
            cls = 'o2' if t.startswith('【記】') else 'o'
            pending = (cls, t)
            continue
        if pending is not None:
            cls, o = pending
            sid = 's' + str(len(body))
            body.append('<div class="pair" id="%s"><div class="%s">%s</div><div class="t">%s</div></div>'
                        % (sid, cls, html.escape(o), html.escape(t)))
            ENTRIES.append(dict(v=vol, o=o, t=t, i=sid))
            pending = None
    prev = HB[vi - 1] if vi > 0 else None
    nxt = HB[vi + 1] if vi + 1 < len(HB) else None
    pager = ''
    if prev:
        pager += '<a href="%s.html">← %s</a>' % (prev, html.escape(prev))
    if nxt:
        pager += '<a href="%s.html">%s →</a>' % (nxt, html.escape(nxt))
    ttl = '四分律行事鈔資持記　句級合編　' + vol
    page_body = ('<h1>' + html.escape(ttl) + '</h1>'
                 '<p class="byline">鈔文（淺褐）與記文（淺藍）逐段並列，每段附白話</p>'
                 + '\n'.join(body) + '<div class="pager">' + pager + '</div>')
    out = SA.page(ttl, page_body, prefix='../',
                  prev_url=(prev + '.html' if prev else None),
                  next_url=(nxt + '.html' if nxt else None),
                  prev_label=prev, next_label=nxt, current_label=vol)
    io.open(os.path.join(OUT, vol + '.html'), 'w', encoding='utf-8').write(out)
    print(vol, '篇', len(toc), '段', len(body))

sp = os.path.join(SITE, 'search')
os.makedirs(sp, exist_ok=True)
payload = 'window.SIDX=window.SIDX||{};window.SIDX["hebian"]=' + json.dumps(
    dict(title='行事鈔資持記・句級合編', entries=ENTRIES), ensure_ascii=False) + ';'
io.open(os.path.join(sp, 'hebian.js'), 'w', encoding='utf-8').write(payload)
print('search/hebian.js', len(ENTRIES), 'entries')
