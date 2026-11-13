# -*- coding: utf-8 -*-
"""資持記 中三上_a (1710-1734) 校閱工具。"""
import os, re, json, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MAT_DIR = os.path.join(ROOT, '校閱_7K')
OUT_DIR = os.path.join(ROOT, 'AI語譯', 'out', '資持記')
BK_DIR = os.path.join(ROOT, '歸檔', '7K卷修正前', '資持記')

LABEL_RE = re.compile(r'^【(\d{4})-(\d{4})】資持記/([^#]+)#(\d+)\s*$')


def parse_mat(n):
    p = os.path.join(MAT_DIR, '校閱_%d.txt' % n)
    s = open(p, encoding='utf-8').read().replace('\r\n', '\n')
    lines = s.split('\n')
    segs = []
    i = 0
    while i < len(lines):
        m = LABEL_RE.match(lines[i].rstrip('\r'))
        if not m:
            i += 1
            continue
        rec = dict(label=lines[i].strip(), n=int(m.group(1)), seg=int(m.group(2)),
                   chunk=m.group(3), idx=int(m.group(4)), orig='', trans='')
        j = i + 1
        if j < len(lines) and lines[j].startswith('【原文】'):
            rec['orig'] = lines[j][4:]
            j += 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith('【譯文】'):
                rec['orig'] += '\n' + lines[j]
                j += 1
        while j < len(lines) and not lines[j].startswith('【譯文】'):
            j += 1
        if j < len(lines):
            rec['trans'] = lines[j][4:]
            j += 1
            while j < len(lines) and lines[j].strip() and not LABEL_RE.match(lines[j].rstrip('\r')):
                rec['trans'] += '\n' + lines[j]
                j += 1
        segs.append(rec)
        i = j
    return segs


def load_out(chunk):
    p = os.path.join(OUT_DIR, chunk + '.txt')
    s = open(p, encoding='utf-8', newline='').read()
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


def apply_edits(chunk, edits):
    o = load_out(chunk)
    segs = list(o['segs'])
    for e in edits:
        i = e['seg'] - 1
        assert 0 <= i < len(segs), (chunk, e['seg'], len(segs))
        t = segs[i]
        cnt = t.count(e['old'])
        if cnt != 1:
            raise SystemExit('COUNT %d %s#%d %r' % (cnt, chunk, e['seg'], e['old'][:60]))
        segs[i] = t.replace(e['old'], e['new'])
    backup(chunk)
    new = o['sep'].join(segs) + (o['trailing'] if o['trailing'] else '')
    open(o['path'], 'w', encoding='utf-8', newline='').write(new)


def backup(chunk):
    os.makedirs(BK_DIR, exist_ok=True)
    src = os.path.join(OUT_DIR, chunk + '.txt')
    dst = os.path.join(BK_DIR, chunk + '_v.txt')
    if os.path.exists(dst):
        return dst
    shutil.copy2(src, dst)
    return dst


def show(n):
    for r in parse_mat(n):
        print('=' * 100)
        print(r['label'], r['chunk'], r['idx'])
        print('【原文】', r['orig'])
        print('【譯文】', r['trans'])


def cmp(n):
    ms = parse_mat(n)
    for r in ms:
        o = load_out(r['chunk'])
        cur = o['segs'][r['idx'] - 1]
        if cur == r['trans']:
            print(r['label'], 'SAME')
        else:
            print(r['label'], 'DIFF')
            print('  MAT:', r['trans'])
            print('  OUT:', cur)


if __name__ == '__main__':
    import sys
    cmd = sys.argv[1]
    if cmd == 'show':
        for n in sys.argv[2:]:
            show(int(n))
    elif cmd == 'cmp':
        for n in sys.argv[2:]:
            cmp(int(n))
