# -*- coding: utf-8 -*-
"""QwenCloud 校閱：逐檔送出材料，存回覆。

設計重點：
1. 可續跑：已存在的 resp 檔跳過。
2. 可優雅停止：建立 `batch_qwen/STOP` 後，不再送出新請求，
   但會等「已在飛」的請求寫完才結束，避免浪費。
3. 併發數由 WORKERS 控制。
"""
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = open(os.path.join(B, '.qwen_key'), encoding='utf-8-sig').read().strip()
BASE = 'https://token-plan.maas.qwencloudapi.com/compatible-mode/v1'
MODEL = 'qwen4-max-preview'
PROMPT = '幫我看看白話譯文有沒有甚麼問題'
OUT = os.path.join(B, 'batch_qwen', os.environ.get('QWEN_OUT', 'r2'))
STOP = os.path.join(B, 'batch_qwen', 'STOP')
WORKERS = int(os.environ.get('QWEN_WORKERS', '12'))
os.makedirs(OUT, exist_ok=True)


def stopped():
    return os.path.exists(STOP)


def run(n):
    src = os.path.join(B, '校閱_10K', '校閱_%03d.txt' % n)
    dst = os.path.join(OUT, 'resp_%03d.txt' % n)
    if os.path.exists(dst) and os.path.getsize(dst) > 200:
        return (n, 'skip')
    if not os.path.exists(src):
        return (n, 'nosrc')
    text = open(src, encoding='utf-8').read()
    head, _, body = text.partition('# 材料開始')
    payload = {
        'model': MODEL,
        'messages': [{'role': 'user',
                      'content': PROMPT + body.strip()}],
        'enable_thinking': True,
        'max_completion_tokens': 65536,
    }
    data = json.dumps(payload).encode()
    for attempt in range(3):
        req = urllib.request.Request(
            BASE + '/chat/completions', data=data,
            headers={'Authorization': 'Bearer ' + KEY,
                     'Content-Type': 'application/json'}, method='POST')
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=1800).read())
            txt = r['choices'][0]['message'].get('content') or ''
            open(dst, 'w', encoding='utf-8').write(txt)
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
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 1912
    todo = [n for n in range(a, b + 1)
            if not (os.path.exists(os.path.join(OUT, 'resp_%03d.txt' % n))
                    and os.path.getsize(os.path.join(OUT, 'resp_%03d.txt' % n)) > 200)]
    print('待跑 %d 檔，併發 %d' % (len(todo), WORKERS), flush=True)

    ok = fail = 0
    inflight = {}
    it = iter(todo)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        # 先填滿
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
                    print('檔%03d %s' % (n, st), flush=True)
            # 只有在沒收到停止訊號時才補新工作
            if not stopped():
                while len(inflight) < WORKERS:
                    try:
                        n = next(it)
                    except StopIteration:
                        break
                    inflight[ex.submit(run, n)] = n
            elif inflight:
                print('收到停止訊號，等待 %d 個在飛請求完成…' % len(inflight), flush=True)
    print('完成 ok=%d fail=%d，耗時 %.0f 秒' % (ok, fail, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
