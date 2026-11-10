# -*- coding: utf-8 -*-
"""Gemini batch 校閱：建 cache、送出批次、收結果。"""
import json, os, sys, time, urllib.request

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = open(os.path.join(B, '.gemini_key'), encoding='utf-8').read().strip()
MODEL = 'gemini-flash-latest'
BASE = 'https://generativelanguage.googleapis.com/v1beta'
HDR = {'x-goog-api-key': KEY, 'Content-Type': 'application/json; charset=utf-8'}


def call(method, url, payload=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=HDR, method=method)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode('utf-8'))


def prompt_text():
    p = os.path.join(B, '校閱批次', '提示詞_白話校閱.md')
    md = open(p, encoding='utf-8').read()
    i = md.find('```text'); j = md.find('```', i + 7)
    return md[i + 7:j].strip() if i >= 0 else md


def cache_name():
    p = os.path.join(B, 'cache_name.txt')
    if os.path.exists(p):
        return open(p, encoding='utf-8').read().strip()
    return None


def submit(files, tag):
    """files: 材料檔路徑清單，回傳 operation name。"""
    cn = cache_name()
    PT = prompt_text()
    reqs = []
    for f in files:
        text = open(f, encoding='utf-8').read()
        body = text.split('# 材料開始', 1)[1].strip() if '# 材料開始' in text else text
        reqs.append({
            'request': {
                # 'cachedContent': cn,  # 實測帶 cache 會 invalid argument
                'contents': [{'role': 'user', 'parts': [{'text': PT}]}, {'role': 'user', 'parts': [{'text': body}]}],
                'generationConfig': {
                    'maxOutputTokens': 65536,
                    'thinkingConfig': {'thinkingLevel': 'high'},
                },
            }
        })
    payload = {'batch': {'displayName': tag, 'inputConfig': {'requests': {'requests': reqs}}}}
    r = call('POST', '%s/models/%s:batchGenerateContent' % (BASE, MODEL), payload)
    return r['name'], len(reqs)


def poll(op, interval=60, max_wait=7200):
    t0 = time.time()
    while time.time() - t0 < max_wait:
        r = call('GET', '%s/%s' % (BASE, op))
        if r.get('done'):
            return r
        time.sleep(interval)
    return r


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'submit'
    if mode == 'submit':
        d = os.path.join(B, '校閱_40K')
        files = [os.path.join(d, '校閱_%03d.txt' % i) for i in range(1, 21)]
        files = [f for f in files if os.path.exists(f)]
        op, n = submit(files, 'round1-20files')
        open(os.path.join(B, 'op_name.txt'), 'w', encoding='utf-8').write(op)
        print(json.dumps({'op': op, 'requests': n}, ensure_ascii=False))
