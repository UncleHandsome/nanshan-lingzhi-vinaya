# -*- coding: utf-8 -*-
"""建立「每段屬於哪一層」的結構資料。

由 CBETA XML 取回每個 block 的角色（orig = 疏/本層，commentary = 記層），
再與 TXT_分卷 的逐段文字做序列對齊，輸出：
  AI語譯/layers/<book>.json   {"<chunk_key>": ["疏","記",...], ...}
層級：律、註、疏、記、鈔、title（篇題/卷題等非正文）。
"""
import os, re, io, json, sys
from collections import Counter
from lxml import etree
from difflib import SequenceMatcher

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
XMLD = os.path.join(B, '_src', 'xml')
OUTD = os.path.join(B, 'AI語譯', 'layers')
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
            if t == 'normal_unicode' and v:
                uni = v
            elif t == 'unicode' and v and uni is None:
                uni = v
        for cp in c.findall('tei:charProp', NS):
            ln = cp.findtext('tei:localName', default='', namespaces=NS)
            val = cp.findtext('tei:value', default='', namespaces=NS)
            if ln == 'normalized form':
                norm = val
            elif ln == 'composition':
                compo = val
        disp = None
        if uni:
            try:
                disp = chr(int(uni.replace('U+', ''), 16))
            except Exception:
                disp = None
        if not disp:
            disp = norm or compo
        if disp and xid:
            m[xid] = disp
    return m


def text_of(el, gaiji):
    parts = []

    def rec(node):
        if node.text:
            parts.append(node.text)
        for ch in node:
            ln = etree.QName(ch).localname
            if ln in INLINE_SKIP:
                pass
            elif ln == 'g':
                ref = (ch.get('ref') or '').lstrip('#')
                parts.append(gaiji.get(ref, ch.text or ''))
            elif ln == 'app':
                lem = ch.find('tei:lem', NS)
                if lem is not None:
                    rec(lem)
                else:
                    for r in ch.findall('tei:rdg', NS):
                        rec(r)
            else:
                rec(ch)
            if ch.tail:
                parts.append(ch.tail)
    rec(el)
    return clean(''.join(parts))


def walk(el, role, blocks, gaiji, skip_mulu=False):
    for ch in el:
        ln = etree.QName(ch).localname
        if ln == 'div':
            t = ch.get('type') or ''
            if t in SKIP_DIV:
                continue
            nr = 'commentary' if t == 'commentary' else ('orig' if t == 'orig' else role)
            has_head = ch.find('head', NS) is not None
            walk(ch, nr, blocks, gaiji, skip_mulu=has_head)
        elif ln == 'juan':
            if ch.get('fun') == 'open':
                label = ''
                mu = ch.find('cb:mulu', NS)
                if mu is not None:
                    label = text_of(mu, gaiji).strip()
                blocks.append({'kind': 'juan', 'text': label, 'role': role})
        elif ln == 'mulu':
            if not skip_mulu:
                t = text_of(ch, gaiji).strip()
                if t:
                    blocks.append({'kind': 'sub', 'text': t, 'role': role})
        elif ln == 'head':
            t = text_of(ch, gaiji).strip()
            if t:
                blocks.append({'kind': 'head', 'text': t, 'role': role})
        elif ln in ('p', 'item'):
            t = text_of(ch, gaiji).strip()
            if t:
                blocks.append({'kind': 'p', 'text': t, 'role': role})
        elif ln == 'l':
            t = text_of(ch, gaiji).strip()
            if t:
                blocks.append({'kind': 'verse', 'text': t, 'role': role})
        elif ln == 'byline':
            t = text_of(ch, gaiji).strip()
            if t:
                blocks.append({'kind': 'byline', 'text': t, 'role': role})
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


# book tag -> (TXT_分卷 dir, xml files, base layer for orig text, layer for commentary)
BOOKS = [
    ('01_行事鈔', '01_行事鈔', ['T40n1804'], '鈔', '記'),
    ('02_戒疏', '02_戒疏', ['X39n0714', 'X40n0714'], '疏', '記'),
    ('03_業疏', '03_業疏', ['X41n0728'], '疏', '記'),
    ('04_比丘尼鈔', '04_比丘尼鈔', ['X40n0724'], '鈔', '記'),
    ('05_拾毗尼義鈔', '05_拾毗尼義鈔', ['X44n0747'], '鈔', '記'),
    ('資持記', '資持記_細分', ['T40n1805'], '記', '記'),
]

LEAD = re.compile(r'^【(律|註|疏|記|經|論|鈔)】')


def norm_key(s):
    s = LEAD.sub('', s.strip())
    s = re.sub(r'[\s\u3000]', '', s)
    s = s.replace('\u25a1', '')
    return s[:24]


def chunk_lines(srcdir):
    """Return [(key, [line, ...]), ...] in the order used by builders."""
    S = os.path.join(B, 'TXT_分卷', srcdir)
    files = sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x))
    out = []
    for f in files:
        if not f.endswith('.txt'):
            continue
        key = f[:-4]
        lines = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        out.append((key, lines))
    return out


def main(only=None):
    os.makedirs(OUTD, exist_ok=True)
    report = {}
    for tag, srcdir, xmls, base, comm in BOOKS:
        if only and tag not in only:
            continue
        blocks = blocks_for(xmls)
        chunks = chunk_lines(srcdir)
        flat = []
        for key, lines in chunks:
            for i, t in enumerate(lines):
                flat.append((key, i, t))
        ak = [norm_key(t) for _, _, t in flat]
        bk = [norm_key(b['text']) for b in blocks]
        sm = SequenceMatcher(None, ak, bk, autojunk=False)
        roles = {}
        matched = 0
        for tagop, a0, a1, b0, b1 in sm.get_opcodes():
            if a0 == a1 or b0 == b1:
                continue
            if a1 - a0 != b1 - b0:
                # 長度不一：逐一配前段，其餘丟棄
                n = min(a1 - a0, b1 - b0)
            else:
                n = a1 - a0
            for k in range(n):
                ai = a0 + k
                bi = b0 + k
                matched += 1
                roles[ai] = (bi, blocks[bi])
        # 分類
        layer_map = {}
        for key, lines in chunks:
            arr = []
            for i, t in enumerate(lines):
                idx = flat.index((key, i, t)) if False else None
                arr.append(None)
            layer_map[key] = arr
        for ai in sorted(roles):
            key, i, t = flat[ai]
            bi, blk = roles[ai]
            L = None
            if blk['kind'] in ('head', 'sub', 'juan', 'byline') and not LEAD.match(t):
                L = 'title'
            if L is None:
                m = LEAD.match(t)
                if m:
                    L = m.group(1)
                elif blk['role'] == 'commentary':
                    L = comm
                else:
                    L = base
                # 記層若文字帶【律】【註】、【疏】以文字為準
                if L in ('律', '註', '疏', '記', '經', '論', '鈔'):
                    pass
            layer_map[key][i] = L
        # 未對齊者補預設層
        for key, lines in chunks:
            for i, v in enumerate(layer_map[key]):
                if v is None:
                    layer_map[key][i] = base
        out = os.path.join(OUTD, tag + '.json')
        io.open(out, 'w', encoding='utf-8').write(json.dumps(layer_map, ensure_ascii=False, indent=0))
        c = Counter()
        for key, arr in layer_map.items():
            c.update(arr)
        report[tag] = dict(blocks=len(blocks), lines=len(flat), matched=matched, dist=dict(c))
        print(tag, 'blocks', len(blocks), 'lines', len(flat), 'matched', matched, dict(c))
    io.open(os.path.join(OUTD, '_report.json'), 'w', encoding='utf-8').write(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1:] or None)
