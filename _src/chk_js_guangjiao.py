import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\jieshu\卷一.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
pairs = re.findall(r'<div class="pair"[^>]*><div class="o">(.*?)</div>', body, re.S)
for kw in ['廣教發起', '發起序', '十門', '篇聚']:
    hits = [(i, re.sub('<[^>]+>', '', p).strip()[:50]) for i, p in enumerate(pairs) if kw in re.sub('<[^>]+>', '', p)]
    print(kw, len(hits), hits[:3])
