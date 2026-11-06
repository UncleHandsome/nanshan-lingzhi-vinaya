import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\diag_ys_shift.py'
s = io.open(p, encoding='utf-8').read()
old = "    print('%-16s %4d %4d %5d %6.2f%s' % r + (flag,))"
new = "    print('%-16s %4s %4s %5s %6s%s' % (r[0], r[1], r[2], r[3], r[4], flag))"
if old in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('fixed')
else:
    print('missing')
