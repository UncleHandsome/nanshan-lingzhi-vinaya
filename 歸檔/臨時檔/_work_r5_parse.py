# -*- coding: utf-8 -*-
"""Round-4 material parser / round-5 builder (temporary helper)."""
import io, os, re, json, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D4 = os.path.join(B, '測試_80K對照', '10K_第4輪')
D3 = os.path.join(B, '測試_80K對照', '10K_第3輪')

LBL = re.compile(r'^【(001-\d{4})】(\S+?)#(\d+)$')

def read(p):
    return io.open(p, encoding='utf-8').read()

def parse_material(text):
    """回傳 [(label_line, sid, src, seg, orig, trans)]，並抓出材料區塊。"""
    lines = text.splitlines()
    # find 材料開始
    try:
        i0 = next(i for i, l in enumerate(lines) if l.strip() == '# 材料開始')
    except StopIteration:
        i0 = 0
    segs = []
    cur = None
    for l in lines[i0 + 1:]:
        if l.strip() == '---' and cur is None:
            break
        m = LBL.match(l.strip())
        if m:
            cur = dict(line=l.strip(), sid=m.group(1), src=m.group(2), seg=int(m.group(3)),
                       orig=None, trans=None)
            segs.append(cur)
            continue
        if cur is None:
            continue
        if l.startswith('【原文】'):
            cur['orig'] = l[4:]
        elif l.startswith('【譯文】'):
            cur['trans'] = l[4:]
    return segs

def main():
    rep = {}
    for fn in sorted(os.listdir(D4)):
        if not fn.endswith('.txt'):
            continue
        t = read(os.path.join(D4, fn))
        segs = parse_material(t)
        bad = [s for s in segs if not s['orig'] or not s['trans']]
        rep[fn] = dict(n=len(segs), first=segs[0]['line'] if segs else None,
                       last=segs[-1]['line'] if segs else None,
                       gaps=[(s['line'], s['orig'] is None, s['trans'] is None) for s in bad])
        print(fn, len(segs), segs[0]['sid'] if segs else '-', segs[-1]['sid'] if segs else '-',
              'bad=%d' % len(bad))
        for b in bad:
            print('   !!', b)
    json.dump(rep, io.open(os.path.join(B, '_work_r5_parse.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
