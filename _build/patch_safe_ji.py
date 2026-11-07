import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\hebian_safe.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("""            zi = ZI.get(idx, [])""",
"""            first_vol = next((it[2] for it in sec['items'] if not SKIP.match(it[0].strip())), vol)
            zi = ZI.get(idx, []) if first_vol == vol else []""")
io.open(p, 'w', encoding='utf-8').write(s)
print('print 記 only in first vol')
