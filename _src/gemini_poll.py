# -*- coding: utf-8 -*-
"""查詢 Gemini batch 狀態，完成後抓結果"""
import io, os, json, urllib.request, urllib.error, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = os.environ.get('GEMINI_API_KEY', '')
WORK = os.path.join(B, 'AI語譯', '_work')
meta = json.load(io.open(os.path.join(WORK, 'gemini_batch.json'), encoding='utf-8'))
name = meta['name']
url = 'https://generativelanguage.googleapis.com/v1beta/%s' % name
req = urllib.request.Request(url, headers={'x-goog-api-key': KEY})
d = json.loads(urllib.request.urlopen(req, timeout=120).read().decode('utf-8'))
state = d.get('metadata', {}).get('state') or d.get('state')
stats = d.get('metadata', {}).get('batchStats', {})
print('state', state, 'stats', stats)
if state and state.endswith('SUCCEEDED'):
    io.open(os.path.join(WORK, 'gemini_result.json'), 'w', encoding='utf-8').write(
        json.dumps(d, ensure_ascii=False, indent=1))
    print('結果已存 gemini_result.json')
    resp = d.get('response', {})
    inl = resp.get('inlinedResponses') or resp.get('inlined_responses') or []
    print('inlined', len(inl))
    for it in inl[:3]:
        key = it.get('metadata', {}).get('key')
        txt = ''
        try:
            txt = it['response']['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            txt = json.dumps(it)[:200]
        print('---', key, txt[:300])
elif state and ('FAILED' in state or 'CANCELLED' in state or 'EXPIRED' in state):
    print(json.dumps(d, ensure_ascii=False)[:800])
