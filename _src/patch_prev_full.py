import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_untrans_prompt.py'
s = io.open(p, encoding='utf-8').read()
old = "- 前一段（僅供理解，不必翻）：%s' % prev[:60]"
new = "- 前一段（完整，僅供理解，不必翻）：%s' % prev"
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('patched prev full')
