import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
lines = io.open(p, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines):
    if 'j = mp[min(acc, len(mp) - 1)]' in l:
        indent = l[:len(l) - len(l.lstrip())]
        lines[i] = (indent + "j = max(mp[min(acc, len(mp) - 1)], mp[min(acc - 1, len(mp) - 1)] + 1) if acc > 0 else mp[0]")
io.open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('cut = max(mp[acc], mp[acc-1]+1)')
