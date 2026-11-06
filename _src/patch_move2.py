import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 移除剛才錯位的插入
start = s.find("    # 整段搬移（manual: 只有 base、沒有 markers）")
if start > 0:
    end = s.find("    # 切點", start)
    s = s[:start] + s[end:]

old = """    pieces = {}
    used = set()"""
new = """    pieces = {}
    used = set()
    # 整段搬移（manual: 只有 base、沒有 markers）
    for e in splits:
        if 'markers' not in e and 'base' in e:
            n0 = int(e['n'])
            for cc in list(by_c):
                if n0 - 1 in by_c[cc]:
                    by_c[cc].remove(n0 - 1)
            by_c.setdefault(int(e['base']), []).append(n0 - 1)
            used.add(n0)"""
if old in s and '整段搬移' not in s:
    s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('move support repositioned')
