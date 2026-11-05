
# -*- coding: utf-8 -*-
import io, os, re, json
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [('04_比丘尼鈔','04_四分律比丘尼鈔_句讀_clean.txt','四分比丘尼鈔'),
         ('05_拾毗尼義鈔','05_四分律拾毗尼義鈔_句讀_clean.txt','四分律拾毗尼義鈔')]
SYS = '你是律宗文獻譯者。下面給你 %d 段《%s》原文（已有句讀）。請逐段譯成現代繁體中文白話。\n輸出恰好 %d 個字串的 JSON 陣列：第 i 項對應第 i 段，一段對一段，不合併、不拆分、不遺漏。\n不得抄錄原文；只輸出 JSON 陣列。'
schema = {"type":"ARRAY","items":{"type":"STRING"}}
lines=[]
meta=[]
for tag, fn, title in BOOKS:
    raw = io.open(os.path.join(D,fn), encoding='utf-8').read()
    paras = [p.strip() for p in re.split(r'\n\s*\n', raw) if p.strip()]
    # 先按句切到 ~200 字，讓譯文顆粒與原文一致
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
    CH=40
    for i in range(0, len(small), CH):
        grp = small[i:i+CH]
        prompt = SYS % (len(grp), title, len(grp)) + '\n【原文】\n' + '\n'.join('%d. %s' % (j+1, t) for j,t in enumerate(grp))
        key = '%s|%d|%d' % (tag, i, len(grp))
        lines.append(json.dumps(dict(key=key, request=dict(contents=[dict(role='user', parts=[dict(text=prompt)])], generationConfig=dict(temperature=0.15, maxOutputTokens=65536, responseMimeType='application/json', responseSchema=schema, thinkingConfig=dict(thinkingLevel='low')))), ensure_ascii=False))
        meta.append(dict(tag=tag, file=fn, title=title, start=i, n=len(grp)))
out = os.path.join(D,'AI語譯','_work','batch_nun_ju.jsonl')
io.open(out,'w',encoding='utf-8').write('\n'.join(lines)+'\n')
io.open(os.path.join(D,'AI語譯','_work','nun_ju_meta.json'),'w',encoding='utf-8').write(json.dumps(meta, ensure_ascii=False, indent=1))
print('requests', len(lines))
