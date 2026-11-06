# -*- coding: utf-8 -*-
import io,json,sys
sys.stdout.reconfigure(encoding='utf-8')
J=json.load(io.open(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix\018.json',encoding='utf-8'))
C={x['c']:x['text'] for x in J['cand']}
for c in [1,2,6,15,20,30,32,33]:
    print('c%d'%c, C.get(c,'(none)')[:70])
print('---out018 used---')
O=json.load(io.open(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix\out_018.json',encoding='utf-8'))
from collections import Counter
cnt=Counter(m['c'] for m in O['map'])
print('n',len(O['map']),'used',sorted(cnt))
print('skipped',[c for c in sorted(C) if c not in cnt][:40])
