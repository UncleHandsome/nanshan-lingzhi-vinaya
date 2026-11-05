
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\user\p4.md'
s = io.open(p, encoding='utf-8').read()
old = "* **答**：各家說法不一，如今的正解是："
new = "* **答**：各家說法不一，若依本宗破除舊說的決定之解："
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
