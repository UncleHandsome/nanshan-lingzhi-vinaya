# -*- coding: utf-8 -*-
import io,json,sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
D=r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
for n in ['001','003','004','005','008','010','011','012']:
    try:
        J=json.load(io.open(D+r'\align_fix\%s.json'%n,encoding='utf-8')) if False else json.load(io.open(D+r'\%s.json'%n,encoding='utf-8'))
        O=json.load(io.open(D+r'\out_%s.json'%n,encoding='utf-8'))
    except Exception as e:
        print(n,'ERR',e); continue
    C={x['c']:x['text'] for x in J['cand']}
    cnt=Counter(m['c'] for m in O['map'])
    skipped=[c for c in sorted(C) if c not in cnt]
    longs=[c for c in skipped if len(C[c])>40]
    print(n,'items',len(J['items']),'cand',len(C),'used',len(cnt),'skipped',len(skipped),'skipped_long',[(c,len(C[c]),C[c][:24]) for c in longs][:6])
