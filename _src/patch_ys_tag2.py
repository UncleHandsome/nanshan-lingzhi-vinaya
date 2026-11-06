import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\punct_yeshu4.py'
s = io.open(p, encoding='utf-8').read()
old = """    seg = jt[pos_map[a]:pos_map[b] + 1].strip()"""
new = """    i0 = pos_map[a]
    back = jt[max(0, i0 - 8):i0]
    mm = re.search(r'【[^】]{1,3}】\\s*$', back)
    if mm:
        i0 = max(0, i0 - 8) + mm.start()
    seg = jt[i0:pos_map[b] + 1].strip()"""
if old in s and 'back = jt' not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('tag-preserve patched')
else:
    print('already or missing')
