import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
J = json.load(io.open(B + r'\013.json', encoding='utf-8'))
O = json.load(io.open(B + r'\out_013.json', encoding='utf-8'))
print('keys', list(O.keys()), 'n', len(O['map']))
cand = {c['c']: c['text'] for c in J['cand']}
it = {i['z']: i['text'] for i in J['items']}
prev = -1
for x in O['map']:
    assert x['c'] >= prev; prev = x['c']
for x in O['map']:
    print('%d -> %3d | %-14s | %s' % (x['z'], x['c'], cand[x['c']][:12], it[x['z']][:18]))
