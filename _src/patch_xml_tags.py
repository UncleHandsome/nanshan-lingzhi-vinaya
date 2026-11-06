import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\xml_tags_yeshu.py'
s = io.open(p, encoding='utf-8').read()
old = """for div in root.iter('{http://www.tei-c.org/ns/1.0}div'):
    typ = div.get('type')
    if typ not in ('orig', 'commentary', 'xu', 'ji'):
        continue
    for p in div.iter('{http://www.tei-c.org/ns/1.0}p'):"""
new = """seen = set()
for div in root.iter():
    if not div.tag.endswith('div'):
        continue
    typ = div.get('type')
    if typ not in ('orig', 'commentary'):
        continue
    for p in div.iter('{http://www.tei-c.org/ns/1.0}p'):
        if id(p) in seen:
            continue
        seen.add(id(p))"""
if old in s and 'seen = set()' not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('div iteration fixed')
else:
    print('already or missing')
