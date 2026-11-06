# -*- coding: utf-8 -*-
"""由 CBETA XML 重建會本（篇1-5 試作）"""
import xml.etree.ElementTree as ET
import os, re, io, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TEI = '{http://www.tei-c.org/ns/1.0}'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
PNAME = ['標宗顯德', '集僧通局', '足數眾相', '受欲是非', '通辨羯磨', '結界方法',
         '僧網大綱', '受戒緣集', '師資相攝', '說戒正儀']


def ptext(p):
    return ''.join(p.itertext()).strip()


root4 = ET.parse(os.path.join(B, '_xml', 'T40n1804.xml')).getroot()
chao = {}          # 篇名 -> [p text]
for d in root4.iter():
    if not d.tag.endswith('div'):
        continue
    head = (d.findtext(TEI + 'head') or '').strip()
    m = re.match(r'^(.*?)篇第', head)
    if not m:
        continue
    key = m.group(1)
    ps = [ptext(p) for p in d.findall(TEI + 'p')]
    ps = [p for p in ps if han(p)]
    chao[key] = ps
print('1804 篇：', [(k, len(v)) for k, v in chao.items()][:8])

root5 = ET.parse(os.path.join(B, '_xml', 'T40n1805.xml')).getroot()
ji = {}
cur = None
for d in root5.iter():
    if not d.tag.endswith('div'):
        continue
    head = (d.findtext(TEI + 'head') or '').strip()
    if head:
        m = re.search(r'釋([\u4e00-\u9fff]{2,6})篇', head)
        if m:
            cur = m.group(1)
    if cur is None:
        continue
    ps = [ptext(p) for p in d.findall(TEI + 'p')]
    ps = [p for p in ps if han(p)]
    if ps:
        ji.setdefault(cur, []).extend(ps)
print('1805 篇：', [(k, len(v)) for k, v in ji.items()])

# 對照 ZI 數量
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
print('\n篇名             XML鈔 分卷鈔  XML記 分卷記')
for i, nm in enumerate(PNAME[:5]):
    xc = len(chao.get(nm, []))
    xj = len(ji.get('釋' + nm if ('釋' + nm) in ji else nm, []))
    print('%-10s %5d %6d %5d %6d' % (nm, xc, len(ZI[i]) and 0 or 0, xj, len(ZI[i])))
