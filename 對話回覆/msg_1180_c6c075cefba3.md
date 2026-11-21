# 對話材料 #1180

- event: assistant/message
- seq: 132570
- time: 1795243568682

---

{"command": "@'\nimport io,os,re,html\nB=r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\np1='三中，《十誦》、《多論》竝云十𤘽盧。彼宗一𤘽盧有二里，止齊二十里。下約山寺上下互明，但在十𤘽盧內，同一法界，故並得安居。恐疑高下不相攝故，特此決之。問：此前太狹，何以引之？答：或彰部異，或證宜狹，或顯諸部皆立分齊，不可通漫，或有別意，學者更裁。《多論》三段：初示量同前。「必使不生疑」者，此示不廣之意。二明得合河道。三明僧尼不同。尼界極齊二里，已外不得。鈔云：必有難緣，可用《僧祇》三由旬內。'\np2='《了論》長圓，或一丈或五尺，趣舉遠近，以彰立相。言水波者，標相屈曲，狀如波焉。自性，即蘭若空處。二繩，謂兩處繩圍，中間連續。四廂，即四向有屋，中有空庭。且列十種，餘即一門、方土、比丘尼、優波塞、垣墻、滿圓、顛狂，並如鈔記具解。「皆」下，疏家總示結略指廣。'\nfor v in ('卷一','卷二','卷三','卷四'):\n p=os.path.join(B,'docs','yeshu',v+'.html'); t=io.open(p,encoding='utf-8').read(); n=0\n def repl(m):\n  global n\n  cls,o,tr=m.group(1),html.unescape(m.group(2)),m.group(3)\n  if '三中十誦多論' in o: n+=1; return '<div class=\"pair %s\"><div class=\"o\">【疏文】%s</div><div class=\"t\">%s</div></div>'%(cls,html.escape(p1),tr)\n  if '了論長圓' in o: n+=1; return '<div class=\"pair %s\"><div class=\"o\">【記文】%s</div><div class=\"t\">%s</div></div>'%(cls,html.escape(p2),tr)\n  return m.group(0)\n t=re.sub(r'<div class=\"pair ([^\"]+)\"><div class=\"o[^\"]*\">(.*?)</div><div class=\"t\">(.*?)</div></div>',repl,t,flags=re.S); io.open(p,'w',encoding='utf-8').write(t); print(v,'fixed',n)\n'@ | Out-File -Encoding utf8 \"$env:TEMP\\ypunct2src.py\"; python -X utf8 \"$env:TEMP\\ypunct2src.py\"; Remove-Item \"$env:TEMP\\ypunct2src.py\" -Force", "description": "Replace two unpunctuated 業疏 sources", "timeoutMs": 120000}