# 對話材料 #1333

- event: assistant/message
- seq: 137029
- time: 1795252062600

---

{"file_path": "C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部\\fix_r013_giants.py", "content": "import io, os, re, html\nB = r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\np = os.path.join(B, 'docs', 'yeshu', '卷四.html')\nt = io.open(p, encoding='utf-8').read()\npat = re.compile(r'<div class=\"pair[^\"]*\"><div class=\"o[^\"]*\">(.*?)</div><div class=\"t\">.*?</div></div>', re.S)\nremoved = []\nfor m in list(pat.finditer(t)):\n    o = html.unescape(re.sub('<[^>]+>', '', m.group(1)))\n    hs = o.replace('【疏文】', '', 1).replace('【記文】', '', 1)\n    if (hs.startswith('然袈裟者但翻為染') and len(hs) > 500) or (hs.startswith('此之四失廣如別疏') and len(hs) > 500) or (hs.startswith('余近問于闐國僧彼既') and len(hs) > 100):\n        t = t[:m.start()] + t[m.end():]\n        removed.append(hs[:20])\nio.open(p, 'w', encoding='utf-8').write(t)\nprint('removed', len(removed), removed)\n"}