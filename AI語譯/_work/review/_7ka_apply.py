# -*- coding: utf-8 -*-
"""Apply 7K 資持記 下一_a edits from JSON.

JSON: {"1858": {"chunk": "13a_下一", "edits": [{"idx":3,"old":"...","new":"...","why":"...","cat":"義理"}]}}
"""
import os, sys, json, shutil, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _7ka_lib as L

def backup(chunk):
    d = os.path.join(L.ROOT, '歸檔', '7K卷修正前', '資持記')
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + '_v.txt')
    if not os.path.exists(dst):
        shutil.copyfile(os.path.join(L.OUT, chunk + '.txt'), dst)
        return dst
    return None

def apply(spec_path):
    spec = json.load(open(spec_path, encoding='utf-8'))
    log = []
    bychunk = {}
    for n in sorted(spec, key=lambda x: (int(x[:4]), x)):
        item = spec[n]
        bychunk.setdefault(item['chunk'], []).extend(
            [(n, e) for e in item['edits']])
    touched = {}
    for chunk, edits in bychunk.items():
        lines, eol = L.read_out(chunk)
        ne = L.para_index(lines)
        for n, e in edits:
            ln = ne[e['idx'] - 1][0]
            cur = lines[ln]
            c = cur.count(e['old'])
            if c != 1:
                raise SystemExit('檔%s seg#%d old count=%d\n%s' % (n, e['idx'], c, e['old']))
            lines[ln] = cur.replace(e['old'], e['new'])
            log.append(dict(n=int(n[:4]), chunk=chunk, idx=e['idx'], cat=e.get('cat', ''),
                            old=e['old'], new=e['new'], why=e.get('why', '')))
        touched[chunk] = (lines, eol)
    for chunk, (lines, eol) in touched.items():
        b = backup(chunk)
        out = os.path.join(L.OUT, chunk + '.txt')
        with open(out, 'w', encoding='utf-8', newline='') as f:
            f.write(eol.join(lines) + eol)
        print('WROTE', chunk, 'backup=', b)
    with open(os.path.join(L.ROOT, 'AI語譯', '_work', 'review', '_7ka_log.jsonl'), 'a', encoding='utf-8') as f:
        for r in log:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('EDITS', len(log))

if __name__ == '__main__':
    apply(sys.argv[1])
