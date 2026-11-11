# -*- coding: utf-8 -*-
"""QwenCloud 校閱：逐檔送出 10KB 材料，存回覆。"""
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = open(os.path.join(B, '.qwen_key'), encoding='utf-8-sig').read().strip()
BASE = 'https://token-plan.maas.qwencloudapi.com/compatible-mode/v1'
MODEL = 'qwen4-max-preview'
OUT = os.path.join(B, 'batch_qwen', 'r1')
os.makedirs(OUT, exist_ok=True)


def run(n):
    src = os.path.join(B, '校閱_10K', '校閱_%03d.txt' % n)
    dst = os.path.join(OUT, 'resp_%03d.txt' % n)
    if os.path.exists(dst) and os.path.getsize(dst) > 200:
        return (n, 'skip', 0)
    text = open(src, encoding='utf-8').read()
    head, _, body = text.partition('# 材料開始')
    body = body.strip()
    payload = {
        'model': MODEL,
        'messages': [{'role': 'user', 'content': head.strip() + chr(10)*2 + body}],
        'enable_thinking': True,
        'thinking_budget': 60000,
        'max_completion_tokens': 65536,
        'temperature': 0.3,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + '/chat/completions', data=data,
                                 headers={'Authorization': 'Bearer ' + KEY,
                                          'Content-Type': 'application/json'}, method='POST')
    for attempt in range(3):
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=1800).read())
            msg = r['choices'][0]['message']
            txt = msg.get('content') or ''
            open(dst, 'w', encoding='utf-8').write(txt)
            return (n, 'ok', r.get('usage', {}).get('completion_tokens', 0))
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:150]
            if e.code == 429:
                time.sleep(20 * (attempt + 1))
                continue
            return (n, 'HTTP%d %s' % (e.code, body), 0)
        except Exception as e:
            time.sleep(5)
    return (n, 'fail', 0)


if __name__ == '__main__':
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    todo = list(range(a, b + 1))
    t0 = time.time()
    ok = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for n, st, tok in ex.map(run, todo):
            if st in ('ok', 'skip'):
                ok += 1
            else:
                print('檔%03d %s' % (n, st), flush=True)
    print('完成 %d/%d，耗時 %.0f 秒' % (ok, len(todo), time.time() - t0))
