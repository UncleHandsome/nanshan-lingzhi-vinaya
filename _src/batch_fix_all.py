
# -*- coding: utf-8 -*-
import io, os, re, json
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [('01_行事鈔','01_行事鈔','四分律刪繁補闕行事鈔'),('03_業疏','03_業疏','四分律刪補隨機羯磨疏'),
         ('02_戒疏','02_戒疏','四分律含注戒本疏'),('資持記','資持記_細分','四分律行事鈔資持記'),
         ('04_比丘尼鈔','04_比丘尼鈔','四分比丘尼鈔'),('05_拾毗尼義鈔','05_拾毗尼義鈔','四分律拾毗尼義鈔')]
schema = {"type":"ARRAY","items":{"type":"STRING"}}
lines=[]; n=0
for tag, src, title in BOOKS:
    RV = os.path.join(D,'AI語譯','review_low_all')
    for f in sorted(os.listdir(RV)):
        if not f.startswith(tag+'__') or not f.endswith('.json'): continue
        key = f[len(tag)+2:-5]
        issues = json.load(io.open(os.path.join(RV,f), encoding='utf-8'))
        if not issues: continue
        S = os.path.join(D,'TXT_分卷',src); T = os.path.join(D,'AI語譯','out',tag)
        sp=[x.strip() for x in io.open(os.path.join(S,key+'.txt'),encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp=[x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(T,key+'.txt'),encoding='utf-8').read()) if x.strip()]
        m=min(len(sp),len(tp))
        src_txt='\n'.join('%d. %s'%(i+1,sp[i]) for i in range(m))
        tr_txt='\n'.join('%d. %s'%(i+1,tp[i]) for i in range(m))
        iss='\n'.join('- 第%s段（%s）：%s｜建議：%s'%(x.get('seg'), x.get('kind',''), x.get('issue','')[:120], x.get('fix','')[:120]) for x in issues)
        prompt='''你是律宗文獻譯者。下面給你《%s》的原文、現有白話譯文與校勘意見。
請依意見修訂譯文，輸出恰好 %d 個字串的 JSON 陣列（第 i 項對應第 i 段），段數不得改變。
只改有問題處，其餘保留；不成立的意見可略過。只輸出 JSON 陣列。
【原文】
%s
【現譯】
%s
【意見】
%s''' % (title, m, src_txt, tr_txt, iss)
        lines.append(json.dumps(dict(key='%s|%s|%d'%(tag,key,m), request=dict(contents=[dict(role='user',parts=[dict(text=prompt)])], generationConfig=dict(temperature=0.15, maxOutputTokens=65536, responseMimeType='application/json', responseSchema=schema, thinkingConfig=dict(thinkingLevel='low')))), ensure_ascii=False))
        n+=1
out=os.path.join(D,'AI語譯','_work','batch_fix_all.jsonl')
io.open(out,'w',encoding='utf-8').write('\n'.join(lines)+'\n')
print('fix requests', n)
