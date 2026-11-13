# -*- coding: utf-8 -*-
"""Apply 7K 資持記 下一_b edits. JSON: {"1883":[{"chunk":"13c_下一","idx":20,"old":"","new":"","why":"","cat":""}]}"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _7kb2_lib as L

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_7kb2_log.jsonl')

def backup(chunk):
    d = os.path.join(L.ROOT, '歸檔', '7K卷修正前', '資持記')
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + '_b.txt')
    if not os.path.exists(dst):
        shutil.copyfile(os.path.join(L.OUT, chunk + '.txt'), dst)
        return dst
    return None

def main(spec_path):
    spec = json.load(open(spec_path, encoding='utf-8'))
    log = []
    bychunk = {}
    for n in sorted(spec, key=lambda x: int(x)):
        for e in spec[n]:
            bychunk.setdefault(e['chunk'], []).append((n, e))
    touched = {}
    for chunk, edits in bychunk.items():
        lines, eol = L.read_out(chunk)
        ne = L.para_index(lines)
        for n, e in edits:
            ln = ne[e['idx'] - 1][0]
            cur = lines[ln]
            c = cur.count(e['old'])
            if c != 1:
                raise SystemExit('檔%s seg#%d old count=%d\nOLD:%s\nCUR:%s' % (n, e['idx'], c, e['old'], cur))
            lines[ln] = cur.replace(e['old'], e['new'])
            log.append(dict(n=int(n), chunk=chunk, idx=e['idx'], cat=e.get('cat', ''),
                            old=e['old'], new=e['new'], why=e.get('why', '')))
        touched[chunk] = (lines, eol)
    for chunk, (lines, eol) in touched.items():
        b = backup(chunk)
        out = os.path.join(L.OUT, chunk + '.txt')
        with open(out, 'w', encoding='utf-8', newline='') as f:
            f.write(eol.join(lines) + eol)
        print('WROTE', chunk, 'lines', len(lines), 'backup=', b)
    with open(LOG, 'a', encoding='utf-8') as f:
        for r in log:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('EDITS', len(log), 'files', len(spec))

if __name__ == '__main__':
    main(sys.argv[1])
