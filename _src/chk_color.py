import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in ['docs/yeshu/卷一.html', 'docs/jieshu/卷二.html']:
    h = io.open(B + '\\' + f.replace('/', '\\'), encoding='utf-8').read()
    ji = h.count('class="o ji"')
    shu = h.count('class="o shu"')
    plain = h.count('class="o"')
    print(f, 'ji', ji, 'shu', shu, 'plain', plain)
