# -*- coding: utf-8 -*-
"""提交 10 篇會本給 Gemini Batch API 審校"""
import io, os, json, glob, urllib.request, urllib.error

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = os.environ.get('GEMINI_API_KEY', '')
MODELS = ['gemini-2.5-flash', 'gemini-flash-latest', 'gemini-2.5-pro', 'gemini-3-pro-preview']
WORK = os.path.join(B, 'AI語譯', '_work')

from docx import Document

files = sorted(glob.glob(os.path.join(B, '白話', '會本_篇0*.docx')))
files.append(os.path.join(B, '白話', '會本_篇10_說戒正儀.docx'))
prompts = []
for f in files:
    name = os.path.basename(f)[:-5]
    d = Document(f)
    body = '\n'.join(p.text.strip() for p in d.paragraphs if p.text.strip())
    prompt = (
        '你是律學與古籍校勘專家。以下是《四分律行事鈔・資持記》會本（%s）的全文，'
        '格式為【鈔NN】…（其白話）…【記NNN】…（其白話），記文依牒詞排在所釋鈔文之後。\n'
        '請逐段審查：\n'
        '1. 每個【記】段是否確實解釋其上方的【鈔】段（前後各一句也要判斷）；\n'
        '2. 有無記文提前（記已解釋下一鈔）或滯後（記仍在解釋上一鈔）；\n'
        '3. 每個【記】的白話是否與該記文相符（有無文白脫節）。\n'
        '只回 JSON：{"issues":[{"loc":"鈔NN/記NNN","type":"提前|滯後|文白脫節|其他","detail":"簡述","fix":"建議"}],'
        '"summary":"整體評語"}。若無問題回 {"issues":[],"summary":"..."}。\n\n=====\n' % name
    ) + body
    prompts.append((name, prompt))

print('篇數', len(prompts), '總字數', sum(len(p) for _, p in prompts))

reqs = []
for name, text in prompts:
    reqs.append({
        'request': {
            'contents': [{'role': 'user', 'parts': [{'text': text}]}],
            'generationConfig': {'temperature': 0.2, 'thinkingConfig': {'thinkingBudget': 24576}}
        },
        'metadata': {'key': name}
    })

payload = json.dumps({'batch': {
    'displayName': 'huiben-review-p1-10',
    'inputConfig': {'requests': {'requests': reqs}}
}}, ensure_ascii=False).encode('utf-8')
print('payload MB', round(len(payload) / 1048576, 2))

last_err = None
for model in MODELS:
    url = 'https://generativelanguage.googleapis.com/v1beta/models/%s:batchGenerateContent' % model
    req = urllib.request.Request(url, data=payload, headers={
        'Content-Type': 'application/json', 'x-goog-api-key': KEY})
    try:
        r = urllib.request.urlopen(req, timeout=180)
        d = json.loads(r.read().decode('utf-8'))
        print('OK model', model)
        print(json.dumps(d, ensure_ascii=False)[:600])
        json.dump({'model': model, 'name': d.get('name'), 'raw': d},
                  io.open(os.path.join(WORK, 'gemini_batch.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'ignore')[:300]
        print('FAIL', model, e.code, body)
        last_err = body
    except Exception as e:
        print('FAIL', model, e)
        last_err = str(e)
