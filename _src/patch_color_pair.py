import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()
old = """                body.append('<div class="pair" id="' + sid_s + '"><div class="o">' + html.escape(it['o']) + '</div>'"""
new = """                _oc = ''
                if it['o'].startswith('【記】'):
                    _oc = ' ji'
                elif it['o'].startswith('【疏】'):
                    _oc = ' shu'
                body.append('<div class="pair" id="' + sid_s + '"><div class="o' + _oc + '">' + html.escape(it['o']) + '</div>'"""
if old in s and "' ji'" not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('color class added')
else:
    print('already or missing')
