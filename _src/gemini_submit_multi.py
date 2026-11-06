# -*- coding: utf-8 -*-
"""每篇一個 Gemini batch job（gemini-3.8-flash，thinking 最大）"""
import io, os, json, glob, urllib.request, urllib.error
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = os.environ.get('GEMINI_API_KEY', '')
MODEL = 'gemini-3.8-flash'
WORK = os.path.join(B, 'AI語譯', '_work')
PAGES = [1, 2, 3, 4, 5, 7, 8, 9, 10]
THINK = 32768

reg = {}
for p in PAGES:
    fs = glob.glob(os.path.join(B, '白話', '會本_篇%02d_*.docx' % p))
    if not fs:
        print('缺檔', p)
        continue
    f = fs[0]
    name = os.path.basename(f)[:-5]
    d = Document(f)
    body = '\n'.join(x.text.strip() for x in d.paragraphs if x.text.strip())
    prompt = (
        '你是律學與古籍校勘專家。以下是《四分律行事鈔・資持記》會本（%s）全文，'
        '格式：【鈔NN】…（白話）…【記NNN】…（白話），記文依牒詞排在所釋鈔文之後。\n'
        '請逐段審查並只回 JSON：\n'
        '1) 每個【記】是否確實在解釋其上方的【鈔】（注意開頭收上一鈔、結尾發起下一鈔的情形）；\n'
        '2) 有無記文提前或滯後（請指出應該移到哪一鈔）；\n'
        '3) 該記的白話是否與該記文相符。\n'
        '輸出：{"issues":[{"loc":"鈔NN/記NNN","type":"提前|滯後|文白脫節|其他","detail":"...","fix":"..."}],'
        '"summary":"..."}；若無問題回 {"issues":[],"summary":"..."}\n\n=====\n' % name
    ) + body
    reqs = [{
        'request': {
            'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
            'generationConfig': {'temperature': 0.2, 'thinkingConfig': {'thinkingBudget': THINK}}
        },
        'metadata': {'key': name}
    }]
    payload = json.dumps({'batch': {
        'displayName': name,
        'inputConfig': {'requests': {'requests': reqs}}
    }}, ensure_ascii=False).encode('utf-8')
    url = 'https://generativelanguage.googleapis.com/v1beta/models/%s:batchGenerateContent' % MODEL
    req = urllib.request.Request(url, data=payload, headers={
        'Content-Type': 'application/json', 'x-goog-api-key': KEY})
    try:
        r = urllib.request.urlopen(req, timeout=180)
        dd = json.loads(r.read().decode('utf-8'))
        nm = dd.get('name')
        print('OK', p, nm, dd.get('metadata', {}).get('state'))
        reg[name] = nm
    except urllib.error.HTTPError as e:
        print('FAIL', p, e.code, e.read().decode('utf-8', 'ignore')[:200])
    except Exception as e:
        print('FAIL', p, e)

json.dump(reg, io.open(os.path.join(WORK, 'gemini_jobs_multi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已提交', len(reg), '個 job')
