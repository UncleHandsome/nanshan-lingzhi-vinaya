# 對話材料 #1138

- event: assistant/message
- seq: 131000
- time: 1795239759835

---

{"command": "@'\nimport io,os,re,html\nB=r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'; p=os.path.join(B,'docs','jieshu','卷一.html'); t=io.open(p,encoding='utf-8').read()\n# load source/translation\ns=io.open(os.path.join(B,'測試','重譯','戒疏','_長段','_材料','00_卷首_0053_02.md'),encoding='utf-8').read(); i=s.rfind('【本次待譯單元】'); j=s.find('【後文背景',i); body=re.sub(r'^■[^\\n]*（原文）\\s*','',s[i+len('【本次待譯單元】'):j]).strip()\no=io.open(os.path.join(B,'重作材料_長段','盲翻材料','戒疏','output2.txt'),encoding='utf-8').read(); m=re.search(r'^# 重跑_戒疏_00_卷首_0053_02\\s*$(.*?)(?=^# 重跑_|\\Z)',o,re.M|re.S); tr=m.group(1).strip();\nif not tr.startswith('【'): tr='【疏文】'+tr\nnew='<div class=\"pair s\"><div class=\"o\">%s</div><div class=\"t\">%s</div></div>'%(html.escape(body).replace('\\n','<br>'),html.escape(tr).replace('\\n','<br>'))\nat=t.find('○九十單提法'); end=t.find('</div></div>',at)+12; t=t[:end]+new+t[end:]; io.open(p,'w',encoding='utf-8').write(t); print('ok',len(re.findall(r'class=\"pair ',t)))\n'@ | Out-File -Encoding utf8 \"$env:TEMP\\jins53b.py\"; python -X utf8 \"$env:TEMP\\jins53b.py\"; Remove-Item \"$env:TEMP\\jins53b.py\" -Force\ngit commit -m \"feat(jieshu): 套用七段重跑譯文\" -- docs/jieshu/卷一.html docs/jieshu/卷四.html\ngit push origin main", "description": "Insert 0053_02 and commit seven outputs", "timeoutMs": 180000}