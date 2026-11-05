
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
old = "        tp = [x.strip() for x in re.split(r'\\n\\s*\\n', tr) if x.strip()]"
new = "        tp = [x.strip() for x in re.split(r'\\n\\s*\\n', tr) if x.strip() and not re.match(r'^\\d+\\s+.*篇\\([上中下][一二三四]\\)$', x.strip())]"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
