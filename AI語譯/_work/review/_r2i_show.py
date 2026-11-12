# -*- coding: utf-8 -*-
"""show segments: python _r2i_show.py ORIG|TRANS|BOTH uniq1 uniq2 ...  或 --resp N"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2i_lib as L

MAP = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2i_map.json'), encoding='utf-8'))
BY = {r['uniq']: r for r in MAP}

def main():
    mode = sys.argv[1]
    keys = sys.argv[2:]
    out = None
    keys2 = []
    for k in keys:
        if k.startswith('--out='):
            out = k.split('=', 1)[1]
        else:
            keys2.append(k)
    keys = keys2
    if keys and keys[0].startswith('--resp'):
        resp = keys[0].split('=')[1] if '=' in keys[0] else keys[1]
        sel = [r for r in MAP if str(r['resp']) == str(resp)]
    else:
        sel = []
        for k in keys:
            if k not in BY:
                mm = re.match(r'^(\d{3,4})-(\d{4})$', k)
                if mm:
                    cand = [r for r in MAP if str(r['resp']) == mm.group(1) and r['uniq'] == mm.group(2)]
                    if cand:
                        sel.append(cand[0]); continue
                print('!! not found', k)
            else:
                sel.append(BY[k])
    buf = []
    for r in sel:
        if mode in ('ORIG', 'BOTH'):
            buf.append('【%s】%s#%d  ORIG: %s' % (r['uniq'], r['chunk'], r['seg'], r['orig']))
        if mode in ('TRANS', 'BOTH'):
            buf.append('【%s】%s#%d  TRANS: %s' % (r['uniq'], r['chunk'], r['seg'], r['trans']))
        buf.append('')
    txt = '\n'.join(buf)
    if out:
        open(out, 'w', encoding='utf-8').write(txt)
        print('wrote', out, len(txt))
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        print(txt)

main()
