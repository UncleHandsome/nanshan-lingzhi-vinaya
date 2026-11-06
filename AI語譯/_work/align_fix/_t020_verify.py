# -*- coding: utf-8 -*-
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix\out_020.json'
raw = io.open(p, encoding='utf-8').read()
print('bytes', len(raw))
O = json.loads(raw)
mp = O['map']
print('keys', list(O), 'n', len(mp))
print('first', mp[:3], 'last', mp[-3:])
print('zs sequential', [m['z'] for m in mp] == list(range(115)))
print('monotone', all(mp[i]['c'] <= mp[i+1]['c'] for i in range(len(mp)-1)))
J = json.load(io.open(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix\020.json', encoding='utf-8'))
cset = {x['c'] for x in J['cand']}
print('all c in cand', all(m['c'] in cset for m in mp))
print('n items file', len(J['items']))
print(raw[:120])
