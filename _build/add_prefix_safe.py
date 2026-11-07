import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\hebian_safe.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("sr(q.add_run(o), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F4EFE2')",
              "sr(q.add_run('【鈔】' + o), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F4EFE2')")
s = s.replace("sr(q.add_run(o), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(q, 'EEF2F6')",
              "sr(q.add_run('【記】' + o), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(q, 'EEF2F6')")
io.open(p, 'w', encoding='utf-8').write(s)
print('prefix added')
