# 對話材料 #1331

- event: assistant/message
- seq: 137015
- time: 1795252029615

---

{"file_path": "C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部\\inspect_r013.py", "content": "import io, re, html\np = r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部\\docs\\yeshu\\卷四.html'\nt = io.open(p, encoding='utf-8').read()\nms = list(re.finditer(r'<div class=\"pair[^\"]*\"><div class=\"o[^\"]*\">(.*?)</div><div class=\"t\">(.*?)</div></div>', t, re.S))\nprint('pairs', len(ms))\nfor i, m in enumerate(ms):\n    o = html.unescape(re.sub('<[^>]+>', '', m.group(1)))\n    if any(o.startswith(x) for x in ('【疏文】然袈裟者', '【記文】四中', '【記文】加法正衣', '【疏文】此之四失', '【疏文】余近問于闐', '【疏文】兩眾沙彌', '【記文】十中初科')):\n        print(i + 1, len(o), repr(o[:80]))\n"}