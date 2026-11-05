
# -*- coding: utf-8 -*-
import io, os, re, json
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'), encoding='utf-8').read()
paras = [p.strip() for p in re.split(r'\n\s*\n', raw) if p.strip()]
small=[]
for p in paras:
    if len(p) <= 220: small.append(p); continue
    buf=''
    for s2 in re.findall(r'[^。！？]*[。！？]?', p):
        if not s2: continue
        if len(buf)+len(s2) > 200 and buf:
            small.append(buf); buf=s2
        else:
            buf += s2
    if buf.strip(): small.append(buf)
print('segments', len(small), 'chars', sum(len(x) for x in small))
SYS = '你是律宗文獻譯者。下面給你 %d 段《四分律刪補隨機羯磨疏》原文（已有句讀）。請逐段譯成現代繁體中文白話。\n輸出恰好 %d 個字串的 JSON 陣列：第 i 項對應第 i 段，一段對一段，不合併、不拆分、不遺漏。\n不得抄錄原文；只輸出 JSON 陣列。'
schema = {"type":"ARRAY","items":{"type":"STRING"}}
lines=[]; meta=[]; CH=40
for i in range(0, len(small), CH):
    grp = small[i:i+CH]
    prompt = SYS % (len(grp), len(grp)) + '\n【原文】\n' + '\n'.join('%d. %s' % (j+1,t) for j,t in enumerate(grp))
    lines.append(json.dumps(dict(key='yeshu|%d|%d' % (i, len(grp)), request=dict(contents=[dict(role='user',parts=[dict(text=prompt)])], generationConfig=dict(temperature=0.15, maxOutputTokens=65536, responseMimeType='application/json', responseSchema=schema, thinkingConfig=dict(thinkingLevel='low')))), ensure_ascii=False))
    meta.append(dict(start=i, n=len(grp)))
out = os.path.join(D,'AI語譯','_work','batch_yeshu_ju.jsonl')
io.open(out,'w',encoding='utf-8').write('\n'.join(lines)+'\n')
io.open(os.path.join(D,'AI語譯','_work','yeshu_ju_segments.json'),'w',encoding='utf-8').write(json.dumps(small, ensure_ascii=False))
print('requests', len(lines))
