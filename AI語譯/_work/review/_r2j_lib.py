# -*- coding: utf-8 -*-
"""r2 資持記 1216-1330 處理共用工具（接續 _r2i_lib.py，備份後綴 _j）。"""
import os, re, json, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
REVIEW_DIR = os.path.join(ROOT, '校閱_10K')
RESP_DIR = os.path.join(ROOT, 'batch_qwen', 'r2')
OUT_DIR = os.path.join(ROOT, 'AI語譯', 'out', '資持記')
BK_DIR = os.path.join(ROOT, '歸檔', 'r2修正前', '資持記')
MAP_PATH = os.path.join(os.path.dirname(__file__), '_r2i_map.json')

LABEL_RE = re.compile(r'^【(\d{3,4})-(\d{4})】(資持記)/([^#]+)#(\d+)\s*$')


def decode(b):
    return b.decode('utf-8')


def load_map():
    with open(MAP_PATH, encoding='utf-8') as f:
        return json.load(f)


def resp_text(n):
    p = os.path.join(RESP_DIR, 'resp_%d.txt' % n)
    if not os.path.exists(p):
        return None
    return decode(open(p, 'rb').read())


def load_out(chunk):
    p = os.path.join(OUT_DIR, chunk + '.txt')
    s = decode(open(p, 'rb').read())
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
    return dict(path=p, s=s, eol=eol, sep=sep, segs=parts, trailing=trailing)


def backup(chunk):
    os.makedirs(BK_DIR, exist_ok=True)
    src = os.path.join(OUT_DIR, chunk + '.txt')
    dst = os.path.join(BK_DIR, chunk + '_j.txt')
    if os.path.exists(dst):
        return dst
    shutil.copy2(src, dst)
    return dst


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
                raise SystemExit('COUNT %d for %s#%d: %r' % (cnt, chunk, segno, e['old'][:80]))
            t = t.replace(e['old'], e['new'])
        segs[i] = t
    backup(chunk)
    new = o['sep'].join(segs) + (o['trailing'] if o['trailing'] else '')
    open(o['path'], 'wb').write(new.encode('utf-8'))
    return [dict(chunk=chunk, seg=e['seg'], old=e['old'], new=e['new'], why=e['why'], note=note) for e in edits]


def seg_text(chunk, seg):
    o = load_out(chunk)
    return o['segs'][seg - 1]
