# -*- coding: utf-8 -*-
"""edit.py batch.json -- apply paragraph edits for a batch of resp files.

batch.json = {
  "edits": [
     {"label":"001-0006", "subs":[["old","new"], ...]},
     {"label":"001-0007", "new":"<full new paragraph>"}
  ],
  "log": [ {"nnn":"001","items":12,"fixed":9,"rej":2,"doubt":1,"note":"..."} ]
}
Resolves label -> out paragraph by exact match of the material 譯文, else fuzzy (>0.6).
Failures are collected and reported; successful edits are still applied.
Backs up chunk file to 歸檔/r3修正前/<book>/ (copy2, only if absent).
Preserves line endings. Appends to fix_r3.tsv and done.tsv.
"""
import os, re, sys, json, difflib, shutil
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
MAT = os.path.join(ROOT, '校閱_10K')
BAK = os.path.join(ROOT, '歸檔', 'r3修正前')
WORK = os.path.join(ROOT, 'AI語譯', '_work', 'review')
LOG = os.path.join(WORK, 'fix_r3.tsv')
DONE = os.path.join(WORK, 'r3_done.tsv')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')

def read_txt(p):
    return open(p, 'rb').read().decode('utf-8-sig')

def parse_mat(nnn):
    t = read_txt(os.path.join(MAT, '校閱_%s.txt' % nnn))
    blocks, cur = {}, None
    for ln in t.split('\n'):
        ln = ln.rstrip('\r')
        m = LBL.match(ln)
        if m:
            cur = m.group(1) + '-' + m.group(2)
            blocks[cur] = {'book': m.group(3), 'chunk': m.group(4), 'src': '', 'tr': ''}
            continue
        if cur is None: continue
        if ln.startswith('【譯文】'): blocks[cur]['tr'] = ln[4:]
        elif ln.startswith('【原文】'): blocks[cur]['src'] = ln[4:]
    return blocks

def apply(batch):
    edits = batch['edits']
    byfile, matcache, errs = {}, {}, []
    for e in edits:
        nnn = e['label'].split('-')[0]
        if nnn not in matcache: matcache[nnn] = parse_mat(nnn)
        b = matcache[nnn][e['label']]
        byfile.setdefault((b['book'], b['chunk']), []).append((e, b))
    nseg = 0
    for (book, chunk), items in byfile.items():
        src = os.path.join(OUT, book, chunk + '.txt')
        lines = read_txt(src).split('\n')
        paras = [(i, s.rstrip('\r')) for i, s in enumerate(lines) if s.rstrip('\r').strip()]
        todo = []
        for e, b in items:
            exact = [i for i, (li, s) in enumerate(paras) if s.strip() == b['tr'].strip()]
            if len(exact) == 1:
                pi = exact[0]
            elif len(exact) > 1:
                errs.append((e['label'], 'AMBIGUOUS %d' % len(exact))); continue
            else:
                best = (-1, 0.0)
                for i, (li, s) in enumerate(paras):
                    r = difflib.SequenceMatcher(None, s, b['tr']).ratio()
                    if r > best[1]: best = (i, r)
                if best[1] < 0.6:
                    errs.append((e['label'], 'NOMATCH %.3f' % best[1])); continue
                pi = best[0]
            li = paras[pi][0]
            cur = lines[li].rstrip('\r')
            new = e.get('new', cur)
            err = None
            for o, n in e.get('subs', []):
                c = new.count(o)
                if c != 1:
                    err = 'SUB count=%d %r' % (c, o); break
                new = new.replace(o, n)
            if err:
                errs.append((e['label'], err + ' || CUR=' + cur)); continue
            if new.strip() == cur.strip():
                continue
            todo.append((e['label'], li, cur, new))
        if not todo: continue
        bp = os.path.join(BAK, book); os.makedirs(bp, exist_ok=True)
        dst = os.path.join(bp, chunk + '.txt')
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        for label, li, cur, new in todo:
            lines[li] = new + ('\r' if lines[li].endswith('\r') else '')
        open(src, 'wb').write('\n'.join(lines).encode('utf-8'))
        with open(LOG, 'a', encoding='utf-8') as f:
            for label, li, cur, new in todo:
                f.write('%s\t%s\t%s\t%d\t%s\n' % (book, chunk, label, li + 1, new))
        nseg += len(todo)
        print('WROTE %s/%s %d: %s' % (book, chunk, len(todo), ','.join(x[0] for x in todo)))
    print('TOTAL FIXED', nseg)
    if errs:
        print('--- ERRORS %d ---' % len(errs))
        for l, m in errs:
            print(l, '|', m)
    if batch.get('log'):
        with open(DONE, 'a', encoding='utf-8') as f:
            for r in batch['log']:
                f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (r['nnn'], r['items'], r['fixed'],
                                                      r['rej'], r['doubt'], r.get('note', '')))
    return len(errs)

if __name__ == '__main__':
    b = json.load(open(sys.argv[1], encoding='utf-8'))
    apply(b)
