# -*- coding: utf-8 -*-
"""套用 _r2k_edits_*.json（備份 _j2）。用法：python _r2k_apply.py _r2k_edits_1263.json [...]
每個 edit：{chunk, seg, old, new, why}，套用前驗 old 在同段恰出現一次。
"""
import os, re, sys, json, shutil
sys.path.insert(0, os.path.dirname(__file__))
import _r2j_lib as L

BK_DIR2 = os.path.join(L.ROOT, '歸檔', 'r2修正前', '資持記')
LOG = os.path.join(os.path.dirname(__file__), '_r2k_log')


def backup2(chunk):
    os.makedirs(BK_DIR2, exist_ok=True)
    src = os.path.join(L.OUT_DIR, chunk + '.txt')
    dst = os.path.join(BK_DIR2, chunk + '_j2.txt')
    if os.path.exists(dst):
        return dst
    shutil.copy2(src, dst)
    return dst


def apply_file(path, dry=False):
    edits = json.load(open(path, encoding='utf-8'))
    by_chunk = {}
    for e in edits:
        if e['old'] == e['new']:
            raise SystemExit('NOOP %s' % e)
        by_chunk.setdefault(e['chunk'], []).append(e)
    done = []
    for chunk, es in by_chunk.items():
        o = L.load_out(chunk)
        segs = list(o['segs'])
        by_seg = {}
        for e in es:
            by_seg.setdefault(int(e['seg']), []).append(e)
        for segno, sub in by_seg.items():
            i = segno - 1
            assert 0 <= i < len(segs), (chunk, segno, len(segs))
            t = segs[i]
            for e in sub:
                c = t.count(e['old'])
                if c != 1:
                    raise SystemExit('COUNT %d %s#%d %r' % (c, chunk, segno, e['old'][:60]))
                t = t.replace(e['old'], e['new'])
                done.append(dict(chunk=chunk, seg=segno, old=e['old'], new=e['new'],
                                 why=e.get('why', ''), src=os.path.basename(path)))
            segs[i] = t
        if not dry:
            backup2(chunk)
            new = o['sep'].join(segs) + (o['trailing'] if o['trailing'] else '')
            open(o['path'], 'wb').write(new.encode('utf-8'))
    return done


if __name__ == '__main__':
    dry = '--dry' in sys.argv
    files = [a for a in sys.argv[1:] if a.endswith('.json')]
    all_done = []
    for f in files:
        all_done += apply_file(f, dry)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG + '.jsonl', 'a', encoding='utf-8') as fh:
        for d in all_done:
            fh.write(json.dumps(d, ensure_ascii=False) + '\n')
    segs = set((d['chunk'], d['seg']) for d in all_done)
    print('edits %d, segs %d, files %d' % (len(all_done), len(segs), len(files)))
