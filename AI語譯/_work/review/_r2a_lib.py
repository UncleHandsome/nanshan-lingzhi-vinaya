# -*- coding: utf-8 -*-
"""r2 1000-1648 共用工具：解析校閱材料、讀寫 out（保留原行尾）、備份、驗證。"""
import os, re, json, shutil, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
REV = os.path.join(ROOT, '校閱_10K')
OUTBASE = os.path.join(ROOT, 'AI語譯', 'out')
BKBASE = os.path.join(ROOT, '歸檔', 'r2修正前')
DONE = os.path.join(ROOT, 'batch_qwen', 'r2_done.txt')

LAB = re.compile(r'^【(\d{4})-(\d{4})】([^/]+)/([^#]+)#(\d+)\s*$')


def rd(p):
    return open(p, 'rb').read()


def decode(b):
    return b.decode('utf-8')


def parse_review(n):
    """回傳 list: batch, seq, book, chunk, seg, orig, trans。原文/譯文可能跨行。"""
    p = os.path.join(REV, '校閱_%d.txt' % n)
    s = decode(rd(p))
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
        self.s = decode(self.raw)
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


def backup(book, chunk, src_path):
    d = os.path.join(BKBASE, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + '_g.txt')
    if os.path.exists(dst):
        return dst
    shutil.copy2(src_path, dst)
    return dst


def apply_edits(book, chunk, edits, dry=False):
    """edits: list of dict(seg=int, old=str, new=str, why=str)
    每條保證 old 在該段恰出現一次；段數不變。回傳 log。"""
    o = Out(book, chunk)
    segs = list(o.segs)
    n_before = len(segs)
    by = {}
    for e in edits:
        by.setdefault(e['seg'], []).append(e)
    for segno, es in by.items():
        i = segno - 1
        if not (0 <= i < len(segs)):
            raise SystemExit('SEG RANGE %s#%d (n=%d)' % (chunk, segno, len(segs)))
        t = segs[i]
        nl0 = t.count('\n') + t.count('\r')
        for e in es:
            c = t.count(e['old'])
            if c != 1:
                raise SystemExit('COUNT %d %s/%s#%d old=%r' % (c, book, chunk, segno, e['old'][:80]))
            t = t.replace(e['old'], e['new'])
        if t.count('\n') + t.count('\r') != nl0:
            raise SystemExit('NEWLINE CHANGED seg %s#%d' % (chunk, segno))
        segs[i] = t
    if len(segs) != n_before:
        raise SystemExit('SEGCOUNT')
    if not dry:
        backup(book, chunk, o.path)
        o.segs = segs
        o.save()
    return [dict(book=book, chunk=chunk, seg=e['seg'], old=e['old'], new=e['new'], why=e.get('why', '')) for e in edits]


def append_done(n):
    with open(DONE, 'a', encoding='utf-8') as f:
        f.write('%d\n' % n)


def done_set():
    if not os.path.exists(DONE):
        return set()
    out = set()
    for ln in decode(rd(DONE)).splitlines():
        ln = ln.strip()
        if not ln:
            continue
        m = re.match(r'^(\d+)$', ln)
        if m:
            out.add(int(m.group(1)))
        m = re.match(r'^(\d+)-(\d+)$', ln)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            out.update(range(a, b + 1))
        m = re.match(r'^[^:]*:(\d+)-(\d+)', ln)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            out.update(range(a, b + 1))
    return out


if __name__ == '__main__':
    n = int(sys.argv[1])
    recs = parse_review(n)
    print('segments', len(recs))
    for r in recs[:3]:
        print(r['seq'], r['book'], r['chunk'], r['seg'], len(r['orig'] or ''), len(r['trans'] or ''))
