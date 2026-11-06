import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
s = io.open(p, encoding='utf-8').read()
old = "        j = mp[min(acc, len(mp) - 1)]"
new = "        j = mp[min(acc, len(mp) - 1)] + 1"
if old in s and "+ 1" not in s.split('cuts.append')[0][-40:]:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('cut +1')
else:
    print('already or missing')
