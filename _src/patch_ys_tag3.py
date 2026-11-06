import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\punct_yeshu4.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("back = jt[max(0, i0 - 8):i0]", "back = jt[max(0, i0 - 24):i0]")
s = s.replace("mm = re.search(r'【[^】]{1,3}】\\s*$', back)", "mm = re.search(r'【[^】]{1,3}】[\\s*]*$', back)")
s = s.replace("i0 = max(0, i0 - 8) + mm.start()", "i0 = max(0, i0 - 24) + mm.start()")
io.open(p, 'w', encoding='utf-8').write(s)
print('window widened')
