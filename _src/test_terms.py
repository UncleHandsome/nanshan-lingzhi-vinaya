import xml.etree.ElementTree as ET, re, os, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TEI = '{http://www.tei-c.org/ns/1.0}'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
root4 = ET.parse(os.path.join(B, '_xml', 'T40n1804.xml')).getroot()
ch = []
for d in root4.iter():
    if not d.tag.endswith('div'):
        continue
    head = (d.findtext(TEI + 'head') or '').strip()
    if head.startswith('通辨羯磨'):
        ch = [''.join(p.itertext()) for p in d.findall(TEI + 'p')]
H = han(''.join(ch))
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
zi = ex.build_zi(ex.sections(), ex.zsecs())[4]

TERM = re.compile(r'「([^」]{2,6})」|([\u4e00-\u9fff]{2,4})者')
cur = 0
anchors = []
for k, (o, t) in enumerate(zi):
    terms = []
    for m in TERM.finditer(o[:60]):
        terms.append(m.group(1) or m.group(2))
    pos = None
    for tm in terms:
        p = H.find(tm, cur)
        if p >= 0 and (pos is None or p < pos):
            pos = p
    if pos is not None:
        cur = pos
        anchors.append(pos)
    else:
        anchors.append(cur)
print('錨點前20', anchors[:20])
print('不同位置數', len(set(anchors)), '/', len(anchors))
