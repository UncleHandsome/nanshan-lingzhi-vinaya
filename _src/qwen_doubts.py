# -*- coding: utf-8 -*-
"""把存疑補判材料（已含提示詞）送 Qwen 判讀，輸出到 回覆/。"""
import io, json, os, re, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '存疑材料', '補判')
OUT = os.path.join(SRC, '回覆')
KEY = open(os.path.join(B, '.qwen_key'), encoding='utf-8-sig').read().strip()
BASE = 'https://token-plan.maas.qwencloudapi.com/compatible-mode/v1'
MODEL = 'qwen4-max-preview'
WORKERS = int(os.environ.get('QWEN_WORKERS', '4'))
STOP = os.path.join(SRC, 'STOP')

os.makedirs(OUT, exist_ok=True)


def run(f):
    src = os.path.join(SRC, f)
    dst = os.path.join(OUT, f.replace('.md', '_回.txt'))
    if os.path.exists(dst) and os.path.getsize(dst) > 200:
        return (f, 'skip')
    text = io.open(src, encoding='utf-8').read()
    payload = {'model': MODEL,
               'messages': [{'role': 'user', 'content': text}],
               'enable_thinking': True,
               'max_completion_tokens': 65536}
    data = json.dumps(payload).encode()
    for attempt in range(3):
        req = urllib.request.Request(BASE + '/chat/completions', data=data,
                                     headers={'Authorization': 'Bearer ' + KEY,
                                              'Content-Type': 'application/json'}, method='POST')
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=2400).read())
            out = r['choices'][0]['message'].get('content') or ''
            io.open(dst, 'w', encoding='utf-8').write(out)
            return (f, 'ok')
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:150]
            if e.code == 429:
                time.sleep(20 * (attempt + 1)); continue
            return (f, 'HTTP%d %s' % (e.code, body))
        except Exception as e:
            time.sleep(5)
    return (f, 'fail')


def main():
    files = sorted(x for x in os.listdir(SRC) if re.match(r'新_補_\d+\.md$', x))
    print('待判', len(files), '份，併發', WORKERS, flush=True)
    ok = fail = 0
    inflight = {}
    it = iter(files)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for f in it:
            inflight[ex.submit(run, f)] = f
            if len(inflight) >= WORKERS:
                break
        while inflight:
            done, _ = wait(inflight, return_when=FIRST_COMPLETED)
            for fu in done:
                f = inflight.pop(fu)
                try:
                    _, st = fu.result()
                except Exception:
                    st = 'err'
                if st in ('ok', 'skip'):
                    ok += 1
                else:
                    fail += 1
                    print(f, st, flush=True)
            if not os.path.exists(STOP):
                while len(inflight) < WORKERS:
                    try:
                        f = next(it)
                    except StopIteration:
                        break
                    inflight[ex.submit(run, f)] = f
    print('完成 ok=%d fail=%d' % (ok, fail), flush=True)


if __name__ == '__main__':
    main()
