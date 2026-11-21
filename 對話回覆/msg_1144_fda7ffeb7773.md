# 對話材料 #1144

- event: assistant/message
- seq: 131290
- time: 1795240422588

---

{"command": "@'\nimport io,os,re,html\nB=r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'; lab={'s':'【疏文】','j':'【記文】','x':'【序文】','z':'【註文】','lv':'【律文】'}\nfor v in ('卷一','卷二','卷三','卷四'):\n p=os.path.join(B,'docs','yeshu',v+'.html'); t=io.open(p,encoding='utf-8').read(); pat=re.compile(r'<div class=\"pair ([^\"]+)\"><div class=\"o\">(.*?)</div><div class=\"t\">(.*?)</div></div>',re.S); c=0\n def repl(m):\n  global c\n  cls,o,tr=m.group(1),html.unescape(m.group(2)),html.unescape(m.group(3)); L=lab.get(cls,'')\n  if L and not o.startswith('【'): o=L+o\n  if L and not tr.startswith('【'): tr=L+tr\n  c+=1\n  return '<div class=\"pair %s\"><div class=\"o\">%s</div><div class=\"t\">%s</div></div>'%(cls,html.escape(o).replace('\\n','<br>'),html.escape(tr).replace('\\n','<br>'))\n t2=pat.sub(repl,t); io.open(p,'w',encoding='utf-8').write(t2); print(v,c)\n'@ | Out-File -Encoding utf8 \"$env:TEMP\\yprefix.py\"; python -X utf8 \"$env:TEMP\\yprefix.py\"; Remove-Item \"$env:TEMP\\yprefix.py\" -Force\ngit commit -m \"fix(yeshu): 每個 pair 補回對應型別標籤\" -- docs/yeshu\ngit push origin main", "description": "Restore labels on all 業疏 pairs", "timeoutMs": 180000}