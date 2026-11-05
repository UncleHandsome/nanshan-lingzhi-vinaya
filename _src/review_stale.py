
# -*- coding: utf-8 -*-
import io, os, re, json
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TARGETS = [('03_業疏','05a_卷一之五'),('02_戒疏','18b_卷四上之三'),('02_戒疏','19b_卷四下之一'),
           ('05_拾毗尼義鈔','03b_卷中之一'),('05_拾毗尼義鈔','04a_卷中之二'),
           ('資持記','11d_中四上'),('資持記','02c_上一下'),('資持記','02f_上一下'),('資持記','03a_上二'),
           ('資持記','02e_上一下'),('03_業疏','03b_卷一之三'),('03_業疏','15a_卷三之四'),('03_業疏','16b_卷三之五'),
           ('04_比丘尼鈔','03b_卷中之上'),('05_拾毗尼義鈔','00_卷首'),('05_拾毗尼義鈔','04b_卷中之二')]
SYS = '你是律宗文獻校勘者。比對《%s》的原文與白話譯文，指出誤譯、漏譯、術語錯誤、分段不合。只回報確實有問題者，沒有問題回空陣列。輸出 JSON 陣列，每項含 seg（段號，1 起）、kind、issue、quote、fix。'
lines=[]
for book, key in TARGETS:
    src = {'資持記':'資持記_細分'}.get(book, book)
    S=os.path.join(D,'TXT_分卷',src,key+'.txt'); T=os.path.join(D,'AI語譯','out',book,key+'.txt')
    if not (os.path.exists(S) and os.path.exists(T)): continue
    sp=[x.strip() for x in io.open(S,encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp=[x.strip() for x in re.split(r'\r?\n\r?\n', io.open(T,encoding='utf-8').read()) if x.strip()]
    n=min(len(sp),len(tp))
    body='\n'.join('%d. 原：%s\n   譯：%s' % (i+1, sp[i][:300], tp[i][:400]) for i in range(n))
    prompt = SYS % book + '\n\n' + body
    lines.append(json.dumps(dict(key='%s|%s|%d'%(book,key,n), request=dict(contents=[dict(role='user',parts=[dict(text=prompt)])], generationConfig=dict(temperature=0.1, maxOutputTokens=32768, responseMimeType='application/json', responseSchema={"type":"ARRAY","items":{"type":"OBJECT","properties":{"seg":{"type":"INTEGER"},"kind":{"type":"STRING"},"issue":{"type":"STRING"},"quote":{"type":"STRING"},"fix":{"type":"STRING"}},"required":["seg","kind","issue","fix"]}}, thinkingConfig=dict(thinkingLevel='low')))), ensure_ascii=False))
out=os.path.join(D,'AI語譯','_work','review_stale.jsonl')
io.open(out,'w',encoding='utf-8').write('\n'.join(lines)+'\n')
print('requests', len(lines))
