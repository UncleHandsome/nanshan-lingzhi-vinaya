import io, os, json, glob, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 1) 篇14 三大群組錨點
fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇14.json')
m = json.load(io.open(fp, encoding='utf-8-sig'))
RANGES = [(87, 97, 14), (98, 109, 15), (323, 327, 59), (413, 415, 72), (416, 425, 73), (426, 436, 74)]
anchors = {}
for a, b, c in RANGES:
    for n in range(a, b + 1):
        anchors[n] = c
m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in anchors]
for n, c in anchors.items():
    m['splits'].append({'n': n, 'base': c})
json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇14 錨點', len(anchors))

# 2) 篇7 記098 多餘「〕」
f = glob.glob(B + r'\白話\會本_篇07_*.docx')[0]
d = Document(f)
for p in d.paragraphs:
    if p.text.strip().startswith('【記098】') and p.text.rstrip().endswith('〕'):
        t = p.text.rstrip()[:-1].rstrip()
        for r in p.runs[1:]:
            r.text = ''
        p.runs[0].text = t
        d.save(f)
        print('篇7 記098 〕已清')
        break

# 3) 古文補字：篇1 記093「斜視曰 ，」；篇1 記104/381「〈〉」
f = glob.glob(B + r'\白話\會本_篇01_*.docx')[0]
d = Document(f)
n = 0
for p in d.paragraphs:
    t = p.text
    t2 = re.sub(r'斜視曰\s*[，,]', '斜視曰眄，', t)
    t2 = t2.replace('〈〉復明受戒具緣', '〈釋相〉復明受戒具緣').replace('〈〉中，以戒本為相', '〈釋相〉中，以戒本為相')
    if t2 != t:
        for r in p.runs[1:]:
            r.text = ''
        if p.runs:
            p.runs[0].text = t2
        else:
            p.add_run(t2)
        n += 1
if n:
    d.save(f)
print('篇1 補字', n)

# 4) 篇30 記019（一）缺閉括號
f = glob.glob(B + r'\白話\會本_篇30_*.docx')[0]
d = Document(f)
for p in d.paragraphs:
    if p.text.strip().startswith('【記019】（一）') and '〕' not in p.text:
        t = p.text.rstrip() + '〕'
        for r in p.runs[1:]:
            r.text = ''
        p.runs[0].text = t
        d.save(f)
        print('篇30 記019 〕已補')
        break
