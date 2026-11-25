# -*- coding: utf-8 -*-
r"""最小連線測試：對 qwen4-max-preview 送一句 "hi"，reasoning effort=low，無工具。

用法：
  python -X utf8 _src\ping_qwen_low.py            # 預設 low
  $env:PING_EFFORT='minimal'; python ...          # 換 effort
  $env:PING_MODEL='qwen4-max-preview'; python ... # 換模型

只印：HTTP 狀態、耗時、輸出文字、錯誤訊息。不寫任何檔案（除 log 外）。
"""
import io
import json
import os
import time
import urllib.error
import urllib.request

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY_FILE = os.environ.get('QWEN_KEY_FILE') or os.path.join(B, 'qwk2.txt')
BASE = 'https://token-plan.maas.qwencloudapi.com/compatible-mode/v1'
MODEL = os.environ.get('PING_MODEL', 'qwen4-max-preview')
EFFORT = os.environ.get('PING_EFFORT', 'low')
MAXTOK = int(os.environ.get('PING_MAXTOK', '16'))


def main():
    key = io.open(KEY_FILE, encoding='utf-8-sig').read().strip()
    payload = {
        'model': MODEL,
        'input': 'hi',
        'reasoning': {'effort': EFFORT},
        'max_output_tokens': MAXTOK,
        'store': False,
        'stream': True,
    }
    req = urllib.request.Request(
        BASE + '/responses',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + key,
                 'Content-Type': 'application/json',
                 'Accept': 'text/event-stream'},
        method='POST')
    print('model=%s effort=%s max_output_tokens=%d' % (MODEL, EFFORT, MAXTOK))
    t0 = time.time()
    text = []
    status = None
    err = None
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            status = r.status
            for raw in r:
                line = raw.decode('utf-8', errors='replace').strip()
                if not line or line.startswith(':') or line.startswith('event:'):
                    continue
                if not line.startswith('data:'):
                    continue
                data = line[5:].strip()
                if data == '[DONE]':
                    break
                try:
                    ev = json.loads(data)
                except Exception:
                    continue
                t = ev.get('type')
                if t == 'response.output_text.delta' and ev.get('delta'):
                    text.append(ev['delta'])
                elif t in ('response.completed', 'response.incomplete', 'response.failed'):
                    st = (ev.get('response') or {}).get('status')
                    print('terminal=%s status=%s' % (t, st))
                    if t == 'response.failed':
                        err = json.dumps((ev.get('response') or {}).get('error'), ensure_ascii=False)[:300]
                elif t == 'error':
                    err = json.dumps(ev.get('error') or ev, ensure_ascii=False)[:300]
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8', errors='replace')[:300]
        err = body
    except Exception as e:
        err = '%s: %s' % (type(e).__name__, str(e)[:200])
    print('耗時 %.1f 秒  HTTP %s' % (time.time() - t0, status))
    print('輸出：%s' % (''.join(text)[:200] or '（無）'))
    if err:
        print('錯誤：%s' % err)


if __name__ == '__main__':
    main()
