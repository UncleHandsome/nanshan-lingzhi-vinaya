# -*- coding: utf-8 -*-
"""r2 資持記 1181-1330 處理共用工具（比照 _r2z4_lib.py，備份後綴 _i）。"""
import os, re, json, shutil, difflib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
REVIEW_DIR = os.path.join(ROOT, '校閱_10K')
OUT_DIR = os.path.join(ROOT, 'AI語譯', 'out', '資持記')
BK_DIR = os.path.join(ROOT, '歸檔', 'r2修正前', '資持記')

LABEL_RE = re.compile(r'^【(\d{3,4})-(\d{4})】(資持記)/([^#]+)#(\d+)\s*$')

def read_text(path):
    return open(path, 'rb').read()

def decode(b):
    return b.decode('utf-8')

def parse_review(n):
    p = os.path.join(REVIEW_DIR, '校閱_%03d.txt' % n)
    s = decode(read_text(p))
    lines = s.split('\n')
    segs = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\r')
        m = LABEL_RE.match(line)
        if not m:
            i += 1
            continue
        label = line
        num, uniq, book, chunk, segno = m.groups()
        rec = dict(label=label, resp=int(num), uniq=uniq, book=book, chunk=chunk,
                   seg=int(segno), orig=None, trans=None, rawtext=s)
        j = i + 1
        while j < len(lines) and not lines[j].startswith('【原文】'):
            j += 1
        if j < len(lines):
            rec['orig'] = lines[j].rstrip('\r')[len('【原文】'):]
            j += 1
            while j < len(lines) and lines[j].strip() != '' and not lines[j].startswith('【譯文】') and not LABEL_RE.match(lines[j].rstrip('\r')):
                rec['orig'] += '\n' + lines[j].rstrip('\r')
                j += 1
        while j < len(lines) and not lines[j].startswith('【譯文】'):
            j += 1
        if j < len(lines):
            rec['trans'] = lines[j].rstrip('\r')[len('【譯文】'):]
            j += 1
            while j < len(lines) and lines[j].strip() != '' and not LABEL_RE.match(lines[j].rstrip('\r')):
                rec['trans'] += '\n' + lines[j].rstrip('\r')
                j += 1
        segs.append(rec)
        i = j
    return segs

def load_out(chunk):
    p = os.path.join(OUT_DIR, chunk + '.txt')
    b = read_text(p)
    s = decode(b)
    eol = '\r\n' if '\r\n' in s else '\n'
    sep = eol + eol
    parts = s.split(sep)
    trailing = ''
    if parts and parts[-1] == '':
        parts = parts[:-1]
        trailing = sep
    elif parts and parts[-1].endswith(eol):
        parts[-1] = parts[-1][:-len(eol)]
        trailing = eol
    return dict(path=p, raw=b, s=s, eol=eol, sep=sep, segs=parts, trailing=trailing)

def norm(s):
    """去掉空白與全形/半形括號差異的粗略正規化，供比對用。"""
    s = s.replace('\r', '').replace('\n', '')
    s = re.sub(r'\s+', '', s)
    return s

def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio()

def best_match(trans, segs):
    best = (-1.0, -1)
    for i, t in enumerate(segs):
        r = sim(trans, t)
        if r > best[0]:
            best = (r, i + 1)
    return best

def apply_edits(chunk, edits, note=''):
    o = load_out(chunk)
    segs = list(o['segs'])
    by_seg = {}
    for e in edits:
        by_seg.setdefault(e['seg'], []).append(e)
    for segno, es in by_seg.items():
        i = segno - 1
        assert 0 <= i < len(segs), (chunk, segno, len(segs))
        t = segs[i]
        for e in es:
            cnt = t.count(e['old'])
            if cnt != 1:
                raise SystemExit('COUNT %d for %s#%d: %r' % (cnt, chunk, segno, e['old'][:60]))
            t = t.replace(e['old'], e['new'])
        segs[i] = t
    backup(chunk)
    new = o['sep'].join(segs) + (o['trailing'] if o['trailing'] else '')
    open(o['path'], 'wb').write(new.encode('utf-8'))
    return [dict(chunk=chunk, seg=e['seg'], old=e['old'], new=e['new'], why=e['why'], note=note) for e in edits]

def backup(chunk):
    os.makedirs(BK_DIR, exist_ok=True)
    src = os.path.join(OUT_DIR, chunk + '.txt')
    dst = os.path.join(BK_DIR, chunk + '_i.txt')
    if os.path.exists(dst):
        return dst
    shutil.copy2(src, dst)
    return dst

def stats(chunk):
    o = load_out(chunk)
    return dict(n=len(o['segs']), eol=repr(o['eol']), lines=o['s'].count('\n'))
