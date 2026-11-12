import sys
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

book, chunk = '01_行事鈔', '08a_卷中之四'
text = read_text(book, chunk)
orig = text
edits = [
 (63, '之所以將前文的句式顛倒而有所不同', '之所以將前文的品位顛倒而有所不同'),
 (63, '在上品四句中各犯一個根本僧殘罪，且每句各自加上不學與無知之罪（共十六罪）；',
      '凡是違犯四根本（四波羅夷）或僧殘罪時，皆各各加上不學與無知二罪；'),
 (64, '造作修習對向境緣之時', '造作營為對向境緣之時'),
 (64, '因此大聖隨順機緣時宜而制戒', '因此大聖隨著這三時而分別制戒'),
 (65, '如果是單純起心動念，那是大乘戒法所制伏的界限。', '如果是單純起心動念（未動身口），制罪便只局限於大乘菩薩戒。'),
]
for idx, old, new in edits:
    text = sub_para(text, idx, old, new, label=f'181#{idx}')
    print('ok', idx, new[:40])
backup(book, chunk)
save(text, book, chunk)
print('saved, changed bytes', len(orig.encode()) , '->', len(text.encode()))
