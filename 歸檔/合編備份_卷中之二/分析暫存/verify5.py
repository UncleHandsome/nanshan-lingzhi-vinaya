# -*- coding: utf-8 -*-
import io, re
import pymupdf
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
pdf = B + r"\白話\PDF\行事鈔資持記句級合編_卷中之二.pdf"
doc = pymupdf.open(pdf)
print('pages', doc.page_count)
txt = ''.join(p.get_text() for p in doc)
print('chars', len(txt))
i = txt.find('為他下，釋出其相')
j = txt.find('摩觸女人戒第二。')
print('記385 首句位置', i, '鈔68 首句位置', j, '順序正確:', 0 <= i < j)
# 找出「僧殘篇中，故失精戒第一」與結尾
print('開頭:', txt[:60].replace('\n','|'))
print('結尾:', txt[-60:].replace('\n','|'))
# 檢查頁碼/頁數與段落關鍵詞存在
for kw in ['故失精戒第一', '摩觸女人戒第二', '說迴僧物入已戒三十']:
    print(kw, kw in txt)
doc.close()
