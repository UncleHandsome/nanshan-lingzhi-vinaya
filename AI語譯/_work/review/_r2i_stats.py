# -*- coding: utf-8 -*-
"""統計：每檔材料段數、意見標記數、改動段數/處數。"""
import os, sys, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RD = os.path.join(ROOT, 'batch_qwen', 'r2')
MAP = json.load(open(os.path.join(HERE, '_r2i_map.json'), encoding='utf-8'))

MARK = re.compile(r'(❗|⚠️|⚠|✏️|✏|★|△|❌|●|【\d{4}-\d{4}】|^\s*\d+[\.、]|^\|)')

def markers(n):
    p = os.path.join(RD, 'resp_%d.txt' % n)
    if not os.path.exists(p):
        return 0
    s = open(p, encoding='utf-8').read()
    c = 0
    for ln in s.split('\n'):
        t = ln.strip()
        if not t or t.startswith('---'):
            continue
        if MARK.search(t):
            c += 1
    return c

def main():
    a, b = int(sys.argv[1]), int(sys.argv[2])
    edits = []
    for f in sorted(glob.glob(os.path.join(HERE, '_r2i_edits_*.json'))):
        edits += json.load(open(f, encoding='utf-8'))
    by_resp = {}
    for e in edits:
        # why 前綴為 uniq
        m = re.match(r'^(\d{4})-(\d{4})', e['why'])
        if m:
            by_resp.setdefault(int(m.group(1)), []).append(e)
    tot_seg = tot_mark = tot_chseg = tot_ch = 0
    for n in range(a, b + 1):
        segs = [r for r in MAP if r['resp'] == n]
        if not segs:
            print('%d  —' % n)
            continue
        chs = sorted(set(e['seg'] for e in by_resp.get(n, [])))
        ch = len(by_resp.get(n, []))
        mk = markers(n)
        print('%d  段%d  標記%d  改段%d  改處%d' % (n, len(segs), mk, len(chs), ch))
        tot_seg += len(segs); tot_mark += mk; tot_chseg += len(chs); tot_ch += ch
    print('TOTAL 段%d 標記%d 改段%d 改處%d' % (tot_seg, tot_mark, tot_chseg, tot_ch))

main()
