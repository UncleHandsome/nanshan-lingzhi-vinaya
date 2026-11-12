# -*- coding: utf-8 -*-
"""r2 1353-1490 專用工具庫（前綴 _zx1353_ 避免與其他批次撞名）。"""
import os, re, json, shutil, difflib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
REV = os.path.join(ROOT, '校閱_10K')
OUTBASE = os.path.join(ROOT, 'AI語譯', 'out')
BKBASE = os.path.join(ROOT, '歸檔', 'r2修正前')
RESP = os.path.join(ROOT, 'batch_qwen', 'r2')
DONE = os.path.join(ROOT, 'batch_qwen', 'r2_done.txt')
WORK = os.path.dirname(os.path.abspath(__file__))
DOUBT = os.path.join(ROOT, '存疑材料', 'r2_存疑')

LAB = re.compile(r'^【(\d{4})-(\d{4})】([^/]+)/([^#]+)#(\d+)\s*$')


def rd(p):
    return open(p, 'rb').read()


def parse_review(n):
    p = os.path.join(REV, '校閱_%d.txt' % n)
    s = rd(p).decode('utf-8')
    lines = s.split('\n')
    segs = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\r')
        m = LAB.match(line)
        if not m:
            i += 1
            continue
        b, q, book, chunk, seg = m.groups()
        rec = dict(batch=int(b), seq=int(q), book=book, chunk=chunk, seg=int(seg),
                   orig=None, trans=None, label=line)
        j = i + 1
        if j < len(lines) and lines[j].startswith('【原文】'):
            buf = [lines[j].rstrip('\r')[len('【原文】'):]]
            j += 1
            while j < len(lines) and lines[j].strip() != '' and not lines[j].startswith('【譯文】') \
                    and not LAB.match(lines[j].rstrip('\r')):
                buf.append(lines[j].rstrip('\r'))
                j += 1
            rec['orig'] = '\n'.join(buf)
        while j < len(lines) and not lines[j].startswith('【譯文】') and not LAB.match(lines[j].rstrip('\r')):
            j += 1
        if j < len(lines) and lines[j].startswith('【譯文】'):
            buf = [lines[j].rstrip('\r')[len('【譯文】'):]]
            j += 1
            while j < len(lines) and lines[j].strip() != '' and not LAB.match(lines[j].rstrip('\r')):
                buf.append(lines[j].rstrip('\r'))
                j += 1
            rec['trans'] = '\n'.join(buf)
        segs.append(rec)
        i = j
    return segs


class Out(object):
    def __init__(self, book, chunk):
        self.book = book
        self.chunk = chunk
        self.path = os.path.join(OUTBASE, book, chunk + '.txt')
        self.raw = rd(self.path)
        self.s = self.raw.decode('utf-8')
        self.eol = '\r\n' if '\r\n' in self.s else '\n'
        sep = self.eol + self.eol
        parts = self.s.split(sep)
        self.trailing = ''
        if parts and parts[-1] == '':
            parts = parts[:-1]
            self.trailing = sep
        self.segs = parts

    def save(self):
        new = (self.eol + self.eol).join(self.segs) + self.trailing
        open(self.path, 'wb').write(new.encode('utf-8'))


def norm(s):
    return ''.join(ch for ch in (s or '') if ch not in ' \t\r\n')


_CACHE = {}


def out_for(book, chunk):
    k = (book, chunk)
    if k not in _CACHE:
        _CACHE[k] = Out(book, chunk)
    return _CACHE[k]


def locate(book, chunk, trans, seg_hint=None, thr=0.94):
    o = out_for(book, chunk)
    mat = norm(trans)
    if seg_hint and 1 <= seg_hint <= len(o.segs):
        r = difflib.SequenceMatcher(None, mat, norm(o.segs[seg_hint - 1])).ratio()
        if r >= thr:
            return seg_hint, r, False
    best = (0.0, -1)
    for i, s in enumerate(o.segs):
        rt = difflib.SequenceMatcher(None, mat, norm(s)).ratio()
        if rt > best[0]:
            best = (rt, i + 1)
    return best[1], best[0], True


def backup(book, chunk, src_path, suffix=''):
    d = os.path.join(BKBASE, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + suffix + '.txt')
    if os.path.exists(dst):
        return dst, False
    shutil.copy2(src_path, dst)
    return dst, True


def apply_batch(book, chunk, edits, dry=False):
    o = Out(book, chunk)
    suffix = '' if book == '資持記' else '_z'
    segs = list(o.segs)
    before = list(segs)
    by = {}
    for e in edits:
        by.setdefault(e['seg'], []).append(e)
    for segno, es in sorted(by.items()):
        i = segno - 1
        if not (0 <= i < len(segs)):
            raise SystemExit('SEG RANGE %s/%s#%d (n=%d)' % (book, chunk, segno, len(segs)))
        t = segs[i]
        nl0 = t.count('\n') + t.count('\r')
        for e in es:
            c = t.count(e['old'])
            if c != 1:
                sm = difflib.SequenceMatcher(None, t, e['old'])
                m = sm.find_longest_match(0, len(t), 0, len(e['old']))
                ctx = t[max(0, m.a - 70):m.a + m.size + 70]
                raise SystemExit('COUNT %d %s/%s#%d old=%r matchlen=%d ctx=%s' % (
                    c, book, chunk, segno, e['old'][:60], m.size, ctx))
            t = t.replace(e['old'], e['new'])
        segs[i] = t
        if t.count('\n') + t.count('\r') != nl0:
            raise SystemExit('NEWLINE seg %s/%s#%d' % (book, chunk, segno))
    if len(segs) != len(before):
        raise SystemExit('SEGCOUNT')
    if not dry:
        dst, created = backup(book, chunk, o.path, suffix)
        o.segs = segs
        o.save()
        return dict(book=book, chunk=chunk, backup=dst, created=created,
                    n=len(segs), eol=repr(o.eol),
                    changed=[i + 1 for i in range(len(segs)) if segs[i] != before[i]],
                    edits=edits)
    return dict(book=book, chunk=chunk, dry=True, n=len(segs), eol=repr(o.eol),
                changed=[i + 1 for i in range(len(segs)) if segs[i] != before[i]], edits=edits)


def append_done(txt):
    with open(DONE, 'a', encoding='utf-8') as f:
        f.write(txt + '\n')
