# 對話材料 #1275

- event: assistant/message
- seq: 136015
- time: 1795250733417

---

{"command": "@'\nimport io,re,html\np=r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部\\docs\\jieshu\\卷二.html'; t=io.open(p,encoding='utf-8').read(); pat=list(re.finditer(r'<div class=\"pair[^\"]*\"[^>]*><div class=\"o[^\"]*\">(.*?)</div>',t,re.S))\nfor i,m in enumerate(pat):\n s=html.unescape(re.sub('<[^>]+>','',m.group(1)))\n if s.strip()=='【律文】身。' or s.strip().startswith('【律文】身'):\n  for j in range(max(0,i-2),min(len(pat),i+3)): print(j,repr(html.unescape(re.sub('<[^>]+>','',pat[j].group(1)))[:100]))\n  break\n'@ | Out-File -Encoding utf8 \"$env:TEMP\\nctxshort.py\"; python -X utf8 \"$env:TEMP\\ctxshort.py\"; Remove-Item \"$env:TEMP\\ctxshort.py\" -Force", "description": "Inspect context of short 律文 fragment"}