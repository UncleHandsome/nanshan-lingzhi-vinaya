# -*- coding: utf-8 -*-
"""檢視 1804/1805 XML 結構，評估以 XML 重建會本"""
import xml.etree.ElementTree as ET
import re, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TEI = '{http://www.tei-c.org/ns/1.0}'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

for name in ['T40n1804', 'T40n1805']:
    root = ET.parse(B + r'\_xml\%s.xml' % name).getroot()
    divs = [d for d in root.iter() if d.tag.endswith('div')]
    print('====', name, 'divs', len(divs))
    for d in divs[:6]:
        typ = d.get('type')
        head = ''.join(d.findtext(TEI + 'head', default='') or '')
        ps = d.findall(TEI + 'p')
        print('  type=%-10s head=%-16s p=%d' % (typ, head[:16], len(ps)))
