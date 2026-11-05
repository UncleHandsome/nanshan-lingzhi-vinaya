
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_user.py'
s = io.open(p, encoding='utf-8').read()
start = s.find("    # 校改表")
end = s.find("    doc.save(out_docx)", start)
assert start > 0 and end > start
s = s[:start] + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('appendix removed, len', len(s))
