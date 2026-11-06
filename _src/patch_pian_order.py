import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()
old = """        if tg != list(range(base, base + len(tg))):
            continue"""
new = """        if tg != list(range(base, base + len(tg))):
            continue
        # 尾片不得越過下一記段的鈔號，否則會造成記號逆序
        nxt = int(am[n]) if n < len(am) and int(am[n]) > 0 else tg[-1]
        if tg[-1] > nxt:
            continue"""
if old in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('next-base guard added')
else:
    print('missing')
