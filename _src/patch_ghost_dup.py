import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 1) 任何「資持記上X」卷頭都不補到前篇
s = s.replace("        if '釋結界篇' in head or '資持記上二' in head:",
              "        if '釋結界篇' in head or '資持記上' in head:")
io.open(p, 'w', encoding='utf-8').write(s)
print('ghost head guard')

# 2) 篇8 記170 開頭若與記169 尾段重複，切掉重複部分
p2 = B + r'\_src\mk_pian_split.py'
s2 = io.open(p2, encoding='utf-8').read()
s2 = s2.replace("""def build(p, splits):""",
"""def strip_dup_tail(p):
    # 篇8：記170 開頭重複記169 尾段
    if p != 8:
        return
    o169, t169 = ZI[7][168]
    o170, t170 = ZI[7][169]
    tail = o169[-60:]
    k = o170.find(tail)
    if k == 0:
        ZI[7][169] = (o170[len(tail):].lstrip('。；，'), t170)


def build(p, splits):""")
s2 = s2.replace("""        out, nc, nz, used = build(p, splits)""",
"""        strip_dup_tail(p)
        out, nc, nz, used = build(p, splits)""")
io.open(p2, 'w', encoding='utf-8').write(s2)
print('dup tail strip')
