import json, io
rows = json.load(io.open('AI語譯/_work/review/_g2_rows.json', encoding='utf-8'))
for d in rows:
    A = d['pairs'][0][0] if d['pairs'] else ''
    B = d['pairs'][0][1] if d['pairs'] else ''
    n = d['current'].count(A) if A else 0
    print(f"{d['idx']:2d} {d['gid']} seg{d['seg']} {d['level']} pairs={len(d['pairs'])} hit={d['hit']} cnt={n} Alen={len(A)} Blen={len(B)}")
    print('   A:', A[:100])
    print('   B:', B[:100])
