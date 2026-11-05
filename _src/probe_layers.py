# -*- coding: utf-8 -*-
"""Probe: can we recover per-line layer roles from CBETA XML?"""
import os, re, io
from lxml import etree

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
XMLD = os.path.join(B, '_src', 'xml')
TEI = 'http://www.tei-c.org/ns/1.0'
CB = 'http://www.cbeta.org/ns/1.0'
NS = {'tei': TEI, 'cb': CB}
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
SKIP_DIV = {'apparatus', 'cbeta-notes', 'xuzang-notes', 'add-notes', 'w'}
INLINE_SKIP = {'note', 'lb', 'pb', 'anchor', 'space', 'caesura', 'milestone', 'figure', 'graphic'}


def clean(s):
    s = s.replace('\r', '').replace('\n', '')
    s = s.replace('\u00a0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return s


def build_gaiji(root):
    m = {}
    for c in root.iter('{%s}char' % TEI):
        xid = c.get(XMLID)
        uni = None; norm = None; compo = None
        for mp in c.findall('tei:mapping', NS):
            t = mp.get('type'); v = (mp.text or '').strip()
            if t == 'normal_unicode' and v: uni = v
            elif t == 'unicode' and v and uni is None: uni = v
        for cp in c.findall('tei:charProp', NS):
            ln = cp.findtext('tei:localName', default='', namespaces=NS)
            val = cp.findtext('tei:value', default='', namespaces=NS)
            if ln == 'normalized form': norm = val
            elif ln == 'composition': compo = val
        disp = None
        if uni:
            try: disp = chr(int(uni.replace('U+', ''), 16))
            except Exception: disp = None
        if not disp: disp = norm or compo
        if disp and xid: m[xid] = disp
    return m


def text_of(el, gaiji):
    parts = []
    def rec(node):
        if node.text: parts.append(node.text)
        for ch in node:
            ln = etree.QName(ch).localname
            if ln in INLINE_SKIP: pass
            elif ln == 'g':
                ref = (ch.get('ref') or '').lstrip('#')
                parts.append(gaiji.get(ref, ch.text or ''))
            elif ln == 'app':
                lem = ch.find('tei:lem', NS)
                if lem is not None: rec(lem)
                else:
                    for r in ch.findall('tei:rdg', NS): rec(r)
            else: rec(ch)
            if ch.tail: parts.append(ch.tail)
    rec(el)
    return clean(''.join(parts))


def walk(el, role, blocks, gaiji, skip_mulu=False):
    for ch in el:
        ln = etree.QName(ch).localname
        if ln == 'div':
            t = ch.get('type') or ''
            if t in SKIP_DIV: continue
            nr = 'commentary' if t == 'commentary' else ('orig' if t == 'orig' else role)
            has_head = ch.find('head', NS) is not None
            walk(ch, nr, blocks, gaiji, skip_mulu=has_head)
        elif ln == 'juan':
            if ch.get('fun') == 'open':
                label = ''
                mu = ch.find('cb:mulu', NS)
                if mu is not None: label = text_of(mu, gaiji).strip()
                blocks.append({'kind': 'juan', 'text': label, 'role': role})
        elif ln == 'mulu':
            if not skip_mulu:
                t = text_of(ch, gaiji).strip()
                if t: blocks.append({'kind': 'sub', 'text': t, 'role': role})
        elif ln == 'head':
            t = text_of(ch, gaiji).strip()
            if t: blocks.append({'kind': 'head', 'text': t, 'role': role})
        elif ln in ('p', 'item'):
            t = text_of(ch, gaiji).strip()
            if t: blocks.append({'kind': 'p', 'text': t, 'role': role})
        elif ln == 'l':
            t = text_of(ch, gaiji).strip()
            if t: blocks.append({'kind': 'verse', 'text': t, 'role': role})
        elif ln == 'byline':
            t = text_of(ch, gaiji).strip()
            if t: blocks.append({'kind': 'byline', 'text': t, 'role': role})
        elif ln in ('lg', 'list'):
            walk(ch, role, blocks, gaiji, skip_mulu=skip_mulu)
        else:
            walk(ch, role, blocks, gaiji, skip_mulu=skip_mulu)


def blocks_for(files):
    out = []
    for fn in files:
        tree = etree.parse(os.path.join(XMLD, fn + '.xml'))
        root = tree.getroot()
        gaiji = build_gaiji(root)
        body = root.find('.//tei:text/tei:body', NS)
        walk(body, None, out, gaiji)
    return out


BOOKS = {
    '01_行事鈔': ('01_四分律刪繁補闕行事鈔', ['T40n1804']),
    '02_戒疏': ('02_四分律含注戒本疏', ['X39n0714', 'X40n0714']),
    '03_業疏': ('03_四分律刪補隨機羯磨疏', ['X41n0728']),
    '04_比丘尼鈔': ('04_四分比丘尼鈔', ['X40n0724']),
    '05_拾毗尼義鈔': ('05_四分律拾毗尼義鈔', ['X44n0747']),
}

for tag, (fname, files) in BOOKS.items():
    bl = blocks_for(files)
    txt = io.open(os.path.join(B, 'TXT', fname + '.txt'), encoding='utf-8').read().split('\n')
    txtl = [l.strip() for l in txt if l.strip()]
    print('===', tag, 'blocks', len(bl), 'txt lines', len(txtl))
    # compare
    same = 0
    for i in range(min(len(bl), len(txtl))):
        if bl[i]['text'] == txtl[i]: same += 1
    print('   equal lines', same, '/', min(len(bl), len(txtl)))
    for i in range(min(len(bl), len(txtl), 400)):
        if bl[i]['text'] != txtl[i]:
            print('   first diff at', i)
            print('     XML:', bl[i]['kind'], bl[i]['role'], bl[i]['text'][:60])
            print('     TXT:', txtl[i][:60])
            break
    from collections import Counter
    print('   roles', Counter([b['role'] for b in bl]))
