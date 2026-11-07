import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
s = io.open(p, encoding='utf-8').read()
old = "        mp = amap.get(key) if amap else None"
new = "        mp = amap.get(key) if (amap and not key.startswith('00_')) else None"
if old in s and "not key.startswith('00_')" not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('patched')
else:
    print('already' if "not key.startswith('00_')" in s else 'missing')
