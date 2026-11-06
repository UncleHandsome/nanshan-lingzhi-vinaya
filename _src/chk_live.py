import urllib.request, re

b = 'https://unclehandsome.github.io/nanshan-lingzhi-vinaya/'
for u in ['yeshu/%E5%8D%B7%E4%B8%80.html', 'style.css']:
    r = urllib.request.urlopen(b + u + '?x=11', timeout=40)
    t = r.read().decode('utf-8', 'ignore')
    print(u, r.status, len(t))
    if u.startswith('yeshu'):
        print('  style ver:', re.findall(r'style\.css\?v=\d+', t)[:1])
        print('  o ji:', t.count('class="o ji"'), ' o shu:', t.count('class="o shu"'))
    else:
        print('  has .o.ji:', '.pair .o.ji' in t)
