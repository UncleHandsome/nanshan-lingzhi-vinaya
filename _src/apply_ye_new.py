# -*- coding: utf-8 -*-
"""把 ye_new.txt 的業疏新譯寫回 AI語譯/out/03_業疏/<chunk>.txt"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '會本材料_11-30', '業疏重譯', 'ye_new.txt')
OUT = os.path.join(B, 'AI語譯', 'out', '03_業疏')
txt = io.open(SRC, encoding='utf-8-sig').read()

dec = json.JSONDecoder()
i = 0
objs = []
while i < len(txt):
    while i < len(txt) and txt[i] in ' \r\n\t,，':
        i += 1
    if i >= len(txt):
        break
    try:
        o, j = dec.raw_decode(txt, i)
        objs.append(o)
        i = j
    except Exception as e:
        print('parse stop at', i, e)
        i += 1

print('解析到', len(objs), '個物件')
applied = {}
for o in objs:
    if not isinstance(o, dict):
        continue
    for chunk, items in o.items():
        if not isinstance(items, dict):
            continue
        fp = os.path.join(OUT, chunk + '.txt')
        if not os.path.exists(fp):
            print('缺檔', chunk)
            continue
        paras = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
        n_ok = 0
        for k, v in items.items():
            try:
                idx = int(k) - 1
            except ValueError:
                continue
            if 0 <= idx < len(paras):
                paras[idx] = str(v).strip()
                n_ok += 1
        io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(paras) + '\n')
        applied[chunk] = n_ok
print('已套用 chunk:', len(applied), '共', sum(applied.values()), '段')
for k, v in sorted(applied.items()):
    print(' ', k, v)
