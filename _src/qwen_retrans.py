# -*- coding: utf-8 -*-
"""Qwen 重譯：逐組送出文言文，收回白話。支援 STOP 檔優雅停止與續跑。"""
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = open(os.path.join(B, '.qwen_key'), encoding='utf-8-sig').read().strip()
BASE = 'https://token-plan.maas.qwencloudapi.com/compatible-mode/v1'
MODEL = 'qwen4-max-preview'
SRC = os.path.join(B, '翻譯_10K')
STOP = os.path.join(SRC, 'STOP')
WORKERS = int(os.environ.get('QWEN_WORKERS', '12'))
PROMPT = '將下面這段文言文翻成白話文\n\n'


def stopped():
    return os.path.exists(STOP)


def run(n):
    sp = os.path.join(SRC, 'src_%04d.txt' % n)
    dp = os.path.join(SRC, 'out_%04d.txt' % n)
    if os.path.exists(dp) and os.path.getsize(dp) > 100:
        return (n, 'skip')
    if not os.path.exists(sp):
        return (n, 'nosrc')
    txt = open(sp, encoding='utf-8').read()
    payload = {
        'model': MODEL,
        'messages': [{'role': 'user', 'content': PROMPT + txt}],
        'enable_thinking': True,
        'thinking_budget': 60000,
        'max_completion_tokens': 65536,
    }
    data = json.dumps(payload).encode()
    for attempt in range(3):
        req = urllib.request.Request(
            BASE + '/chat/completions', data=data,
            headers={'Authorization': 'Bearer ' + KEY,
                     'Content-Type': 'application/json'}, method='POST')
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=2400).read())
            out = r['choices'][0]['message'].get('content') or ''
            open(dp, 'w', encoding='utf-8').write(out)
            return (n, 'ok')
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(20 * (attempt + 1))
                continue
            return (n, 'HTTP%d' % e.code)
        except Exception:
            time.sleep(5)
    return (n, 'fail')


def main():
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 764
    todo = []
    for n in range(a, b + 1):
        dp = os.path.join(SRC, 'out_%04d.txt' % n)
        if not (os.path.exists(dp) and os.path.getsize(dp) > 100):
            todo.append(n)
    print('待譯 %d 組，併發 %d' % (len(todo), WORKERS), flush=True)
    ok = fail = 0
    inflight = {}
    it = iter(todo)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for n in it:
            inflight[ex.submit(run, n)] = n
            if len(inflight) >= WORKERS:
                break
        while inflight:
            done, _ = wait(inflight, return_when=FIRST_COMPLETED)
            for f in done:
                n = inflight.pop(f)
                try:
                    _, st = f.result()
                except Exception:
                    st = 'err'
                if st in ('ok', 'skip'):
                    ok += 1
                else:
                    fail += 1
                    print('組%04d %s' % (n, st), flush=True)
            if not stopped():
                while len(inflight) < WORKERS:
                    try:
                        n = next(it)
                    except StopIteration:
                        break
                    inflight[ex.submit(run, n)] = n
            elif inflight:
                print('收到 STOP，等待 %d 個在飛請求完成' % len(inflight), flush=True)
    print('完成 ok=%d fail=%d，耗時 %.0f 秒' % (ok, fail, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
