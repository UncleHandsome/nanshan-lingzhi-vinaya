# -*- coding: utf-8 -*-
import io,json,sys
sys.stdout.reconfigure(encoding='utf-8')
p=r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_ai\020.json'
J=json.load(io.open(p,encoding='utf-8'))
print(type(J), list(J)[:10] if isinstance(J,dict) else len(J))
if isinstance(J,dict):
    print({k:(len(v) if isinstance(v,list) else v) for k,v in J.items() if k!='items' and k!='cand'})
    print('items',len(J.get('items',[])),'cand',len(J.get('cand',[])))
    print('first item', str(J['items'][0])[:200])
    print('first cand', str(J['cand'][0])[:200])
o=r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_ai\out_020.json'
O=json.load(io.open(o,encoding='utf-8'))
print('out keys', list(O) if isinstance(O,dict) else len(O))
print(str(O)[:500])
