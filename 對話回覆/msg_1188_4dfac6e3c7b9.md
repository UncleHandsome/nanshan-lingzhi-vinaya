# 對話材料 #1188

- event: assistant/message
- seq: 132865
- time: 1795244188320

---

{"command": "@'\nimport io,os,re,html\nB=r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\nfor v in ('卷上','卷中','卷下'):\n t=io.open(os.path.join(B,'docs','xingshichao',v+'.html'),encoding='utf-8').read(); print(v,'鈔文',t.count('【鈔文】'),'記文',t.count('【記文】'),'疏文',t.count('【疏文】'))\n m=re.search(r'【鈔文】',t); print(repr(t[m.start()-100:m.start()+100]) if m else '')\n'@ | Out-File -Encoding utf8 \"$env:TEMP\\xlabels.py\"; python -X utf8 \"$env:TEMP\\xlabels.py\"; Remove-Item \"$env:TEMP\\xlabels.py\" -Force", "description": "Inspect 行事鈔 labels"}