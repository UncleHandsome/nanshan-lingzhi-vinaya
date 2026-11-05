
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
old = """        for mode, label in (('dui', '對照本'), ('qian', '全白話本')):
            path = os.path.join(OUT, '行事鈔_白話%s_%s.docx' % (label, v))"""
new = """        for mode, label in (('dui', '白話對照本'), ('qian', '全白話本')):
            path = os.path.join(OUT, '行事鈔_%s_%s.docx' % (label, v))"""
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
