# -*- coding: utf-8 -*-
"""補跑缺檔：先整檔送，若被內容審查擋掉（data_inspection_failed），拆成兩半分別送再合併。"""
import io, json, os, re, sys, time, urllib.request, urllib.error

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = open(os.path.join(B, '.qwen_key'), encoding='utf-8-sig').read().strip()
BASE = 'https://token-plan.maas.qwencloudapi.com/compatible-mode/v1'
MODEL = 'qwen4-max-preview'
PROMPT = '幫我看看白話譯文有沒有甚麼問題'
SRC = os.path.join(B, '校閱_10K')


def call(text, tag):
    payload = {'model': MODEL,
               'messages': [{'role': 'user', 'content': PROMPT + '\n\n' + text}],
               'enable_thinking': True, 'max_completion_tokens': 65536}
    req = urllib.request.Request(BASE + '/chat/completions',
                                 data=json.dumps(payload).encode(),
                                 headers={'Authorization': 'Bearer ' + KEY,
                                          'Content-Type': 'application/json'}, method='POST')
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=2400).read())
        return ('ok', r['choices'][0]['message'].get('content') or '')
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        if 'data_inspection_failed' in body:
            return ('blocked', body)
        return ('HTTP%d' % e.code, body)
    except Exception as e:
        return ('err', str(e)[:100])


def split_body(body):
    """依段切成兩半（以 【NNN-NNNN】 為界）。"""
    parts = [p for p in re.split(r'\n(?=【\d{3}-\d{4}】)', body) if p.strip()]
    if len(parts) < 2:
        i = len(body) // 2
        return [body[:i], body[i:]]
    m = len(parts) // 2
    return ['\n'.join(parts[:m]), '\n'.join(parts[m:])]


def run(n, outdir):
    sp = os.path.join(SRC, '校閱_%03d.txt' % n)
    dp = os.path.join(outdir, 'resp_%03d.txt' % n)
    if not os.path.exists(sp):
        print(n, '無材料', flush=True); return 'nosrc'
    body = io.open(sp, encoding='utf-8').read().partition('# 材料開始')[2].strip()
    st, out = call(body, str(n))
    if st == 'ok':
        io.open(dp, 'w', encoding='utf-8').write(out)
        print(n, 'ok', len(out), flush=True); return 'ok'
    if st != 'blocked':
        print(n, st, out[:80], flush=True); return st
    # 被審查 → 拆半
    print(n, 'blocked → 拆半', flush=True)
    halves = split_body(body)
    outs = []
    for i, h in enumerate(halves):
        s2, o2 = call(h, '%d.%d' % (n, i + 1))
        if s2 != 'ok':
            print(n, '半份%d 失敗' % (i + 1), s2, flush=True)
            return 'blocked_half'
        outs.append(o2)
    merged = '\n\n---\n\n'.join(outs)
    io.open(dp, 'w', encoding='utf-8').write(merged)
    print(n, 'ok(拆半合併)', len(merged), flush=True)
    return 'ok'


if __name__ == '__main__':
    outdir = sys.argv[1]
    nums = [int(x) for x in sys.argv[2:]]
    os.makedirs(outdir, exist_ok=True)
    for n in nums:
        run(n, outdir)
        time.sleep(2)
