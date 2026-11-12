import sys
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

# ---------- 188 ----------
book, chunk = '01_行事鈔', '08b_卷中之四'
text = read_text(book, chunk)
text = sub_para(text, 37, '乃因安立之法各有差異故', '乃因這十三條罪各自成聚、與其餘篇聚各別不濫之故', label='188-0006')
backup(book, chunk); save(text, book, chunk)
print('188 saved')

# ---------- 192 ----------
book, chunk = '01_行事鈔', '08c_卷中之四'
text = read_text(book, chunk)
edits = [
 (2, '羯磨者如前作法，和白言：「大德僧伽請聽！', '羯磨師依照前述的作法，在僧眾和合之下宣告說：「大德僧伽請聽！'),
 (3, '所以經文說：自今以後', '所以律文說：自今以後'),
 (6, '也就是初篇（波羅夷）、二篇（僧殘）的前方便罪', '也就是初篇（波羅夷）、二篇（僧殘）之下的方便罪'),
 (7, '指盜取僧團的飲食器具、十方現前僧物', '指盜取僧團的飲食等常住之物（十方常住物）、十方現前僧物'),
 (7, '一人穿衣、一人裸露而相互摩觸，構成僧殘的境界；',
     '一人穿衣、一人裸露而相互摩觸；在僧殘戒的境緣上造作罪行（如為他人出精、摩觸黃門二形等）；'),
 (7, '灌洗下部、裸露身體行走', '以酥油灌注下身、裸露身體行走'),
 (7, '以瞋恨心撕裂撕破三衣及鉢、破壞佛塔等', '以瞋恨心撕裂三衣、砸破鉢、破壞佛塔等'),
]
for idx, old, new in edits:
    text = sub_para(text, idx, old, new, label=f'192#{idx}')
backup(book, chunk); save(text, book, chunk)
print('192 saved')
