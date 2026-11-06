import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 在組裝 pieces 前，處理「整段搬移」手動條目
s = s.replace("""    # 切點
    pieces = {}""",
"""    # 整段搬移（manual: 只有 base、沒有 markers）
    for e in splits:
        if 'markers' not in e and 'base' in e:
            n = int(e['n'])
            for cc in list(by_c):
                if n - 1 in by_c[cc]:
                    by_c[cc].remove(n - 1)
            by_c.setdefault(int(e['base']), []).append(n - 1)
            used.add(n)

    # 切點
    pieces = {}""")
io.open(p, 'w', encoding='utf-8').write(s)
print('move support added')
