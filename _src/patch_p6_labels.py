import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
s = io.open(p, encoding='utf-8').read()

# 1) 記20 切點
s = s.replace("    16: ['大界中'],", "    16: ['大界中'],\n    20: ['戒場中'],")
# 2) PLAN c6 加記20後半
s = s.replace("    6: [(21, 0), (22, 0)],", "    6: [(20, 1), (21, 0), (22, 0)],")
# 3) 標籤：多段用 前/中/後 或 一/二/三/四
old = """        tag = '【記%03d】' % n + ('（後半）' if part else '') if len(seq) > 1 else '【記%03d】' % n"""
new = """        if len(seq) > 1:
            if len(seq) == 2:
                sub = ['前半', '後半'][part]
            elif len(seq) == 3:
                sub = ['前', '中', '後'][part]
            else:
                sub = ['一', '二', '三', '四', '五'][part] if part < 5 else str(part + 1)
            tag = '【記%03d】（%s）' % (n, sub)
        else:
            tag = '【記%03d】' % n"""
if old in s:
    s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('labels + 記20 split')
