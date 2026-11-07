import io, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = json.load(io.open(B + r'\docs\nav.json', encoding='utf-8'))
for b in d['books']:
    if b['out'] == 'jieshu':
        print('戒疏卷一：', [s[1] for s in b['vols'][0]['secs']][:10])
h = io.open(B + r'\docs\yichao\卷上.html', encoding='utf-8').read()
m = re.search(r'<script[^>]*nav\.js[^>]*>', h)
print('義鈔 script：', m.group(0) if m else '無')
print('義鈔 h2：', len(re.findall(r'<h2 class="sec"', h)),
      'span：', len(re.findall(r'span id="p', h)))
print('義鈔 p1 上下文：', re.sub('<[^>]+>', ' ', h[h.find('id="p1"'):h.find('id="p1"') + 160])[:120])
