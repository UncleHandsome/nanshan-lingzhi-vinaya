# -*- coding: utf-8 -*-
"""r2 資持記 926-999 處理共用工具。

- 解析 校閱_10K/校閱_NNN.txt 的段（label / chunk / seg / 原文 / 材料譯文）
- 解析 AI語譯/out/資持記/<chunk>.txt 的段（以空行分隔）
- 驗證、備份、套用最小替換
"""
import os, re, json, shutil, hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
REVIEW_DIR = os.path.join(ROOT, '校閱_10K')
OUT_DIR = os.path.join(ROOT, 'AI語譯', 'out', '資持記')
BK_DIR = os.path.join(ROOT, '歸檔', 'r2修正前', '資持記')

LABEL_RE = re.compile(r'^【(\d{3})-(\d{4})】(資持記)/([^#]+)#(\d+)\s*$')

def read_text(path):
    b = open(path, 'rb').read()
    return b

def decode(b):
    return b.decode('utf-8')

def parse_review(n):
    """回傳 list of dict: label, file, chunk, seg, orig, trans, raw_block"""
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
                   seg=int(segno), orig=None, trans=None)
        j = i + 1
        while j < len(lines) and not lines[j].startswith('【原文】'):
            j += 1
        if j < len(lines):
            rec['orig'] = lines[j].rstrip('\r')[len('【原文】'):]
            j += 1
            # 原文可能跨行（單換行），直到空行或譯文標記
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
    # 保留結尾：若檔尾只有一個 eol，split 後最後為 ''
    parts = s.split(sep)
    trailing = ''
    if parts and parts[-1] == '':
        parts = parts[:-1]
        trailing = sep
    elif parts and parts[-1].endswith(eol):
        parts[-1] = parts[-1][:-len(eol)]
        trailing = eol
    return dict(path=p, raw=b, s=s, eol=eol, sep=sep, segs=parts, trailing=trailing)

_SEG_INDEX_CACHE = {}

def get_segments():
    """回傳 {(chunk, seg): {'orig','trans','resp'}}"""
    if _SEG_INDEX_CACHE:
        return _SEG_INDEX_CACHE
    idx = {}
    for n in range(926, 1000):
        p = os.path.join(REVIEW_DIR, '校閱_%03d.txt' % n)
        if not os.path.exists(p):
            continue
        for rec in parse_review(n):
            idx[(rec['chunk'], rec['seg'])] = rec
    _SEG_INDEX_CACHE.update(idx)
    return idx

def seg_texts(chunk):
    o = load_out(chunk)
    return o, o['segs']

def apply_edits(chunk, edits, note=''):
    """edits: list of dict(seg=int, old=str, new=str, why=str)
    對 out 檔逐段做最小替換；每條驗證 old 在該段恰出現一次。
    回傳 log list。套用前若無備份則備份。
    """
    o = load_out(chunk)
    segs = list(o['segs'])
    log = []
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
    # 寫回
    backup(chunk)
    new = o['sep'].join(segs) + (o['trailing'] if o['trailing'] else '')
    open(o['path'], 'wb').write(new.encode('utf-8'))
    for e in edits:
        log.append(dict(chunk=chunk, seg=e['seg'], old=e['old'], new=e['new'], why=e['why'], note=note))
    return log

def backup(chunk):
    os.makedirs(BK_DIR, exist_ok=True)
    base = chunk + '.txt'
    dst = os.path.join(BK_DIR, chunk + '_f.txt')
    if os.path.exists(dst):
        return dst  # 已備份過，不覆蓋
    shutil.copy2(os.path.join(OUT_DIR, base), dst)
    return dst

def stats(chunk):
    o = load_out(chunk)
    return dict(n=len(o['segs']), eol=repr(o['eol']), lines=o['s'].count('\n'))
