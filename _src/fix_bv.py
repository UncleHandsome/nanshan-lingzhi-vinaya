
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("        num = int(key.split('_')[0])", "        num = int(re.match(r'^(\\d+)', key).group(1))")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
