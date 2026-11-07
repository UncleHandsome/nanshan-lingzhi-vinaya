# -*- coding: utf-8 -*-
"""檢查側欄每個錨點是否真的指向對應內容（標題文字須出現在錨點附近）"""
import io, os, re, json, html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')
nav = json.load(io.open(os.path.join(SITE, 'nav.json'), encoding='utf-8'))
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

problems = []
ok = 0
for bk in nav['books']:
    out = bk['out']
    for v in bk['vols']:
        page = os.path.join(SITE, out, v['v'] + '.html')
        if not os.path.exists(page):
            continue
        h = io.open(page, encoding='utf-8').read()
        body = h[h.find('<main>'):]
        # 切出每個錨點之後的文字
        marks = [(m.start(), m.group(1)) for m in re.finditer(r'id="(p\d+)"', body)]
        for idx, (pos, pid) in enumerate(marks):
            end = marks[idx + 1][0] if idx + 1 < len(marks) else len(body)
            seg = re.sub('<[^>]+>', '', body[pos:min(end, pos + 1200)])
            seg_h = han(seg)
            # 找到對應的側欄標籤
            sec = next((s for s in v.get('secs', []) if s[0] == pid), None)
            if not sec:
                continue
            label = sec[1]
            key = han(re.sub(r'^序文：|^（續）', '', label))
            if not key:
                continue
            hit = key[:10] in seg_h or key in seg_h
            if hit:
                ok += 1
            else:
                problems.append((out, v['v'], pid, label[:24], seg[:40]))
print('錨點檢查：正確 %d、可疑 %d' % (ok, len(problems)))
for p in problems[:15]:
    print('  %-10s %-6s %-4s 標籤=%-24s 錨點後文=%s' % p)
