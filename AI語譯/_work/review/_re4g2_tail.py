import json
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
for n in (11, 62, 68, 98, 101, 112, 9, 19):
    d = rows[n]
    c = d['current']
    print(n, repr(c[-30:]))
    print('   tail ascii codes:', [hex(ord(ch)) for ch in c[-4:]])
