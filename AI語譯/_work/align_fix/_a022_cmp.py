# -*- coding: utf-8 -*-
import io, csv, json, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = B + r'\AI語譯\_work\align_fix'
for num, sec in [('017', 16), ('018', 17), ('019', 18), ('020', 19), ('021', 20)]:
    pass

def csv_map(secname):
    p = B + r'\合編材料\%s.csv' % secname
    rows = list(csv.reader(io.open(p, encoding='utf-8-sig')))
    ji = [r for r in rows[1:] if r[0] == '記']
    return [r[4].strip() for r in ji], [r[2][:20] for r in ji]

for secname, outfile in [('篇17_二衣總別', 'out_018.json'), ('篇19_鉢器制聽', None)]:
    m, heads = csv_map(secname)
    print('===', secname, 'ji', len(m))
    if outfile:
        J = json.load(io.open(D + '\\' + outfile, encoding='utf-8'))
        mp = [x['c'] for x in J['map']]
        print('out len', len(mp))
        # print runs
        runs = []
        prev = None
        for i, c in enumerate(mp):
            if c != prev:
                runs.append((i, c))
                prev = c
        print('runs', runs)
        # csv runs
        prev = None; runs2 = []
        for i, v in enumerate(m):
            if v != prev:
                runs2.append((i, v)); prev = v
        print('csv runs', runs2)
