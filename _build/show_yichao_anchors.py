import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')
nav = json.load(io.open(os.path.join(SITE, 'nav.json'), encoding='utf-8'))
for bk in nav['books']:
    if bk['out'] != 'yichao':
        continue
    for v in bk['vols']:
        h = io.open(os.path.join(SITE, 'yichao', v['v'] + '.html'), encoding='utf-8').read()
        body = h[h.find('<main>'):]
        marks = [(m.start(), m.group(1)) for m in re.finditer(r'id="(p\d+)"', body)]
        print('=====', v['v'], '錨點', len(marks))
        for idx, (pos, pid) in enumerate(marks[:8]):
            end = marks[idx + 1][0] if idx + 1 < len(marks) else len(body)
            seg = re.sub('<[^>]+>', ' ', body[pos:min(end, pos + 300)])
            seg = re.sub(r'\s+', ' ', seg).strip()
            label = next((s[1] for s in v['secs'] if s[0] == pid), '?')
            print('%s 側欄=%-8s 頁面=%s' % (pid, label[:10], seg[:70]))
