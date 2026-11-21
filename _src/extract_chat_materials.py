# -*- coding: utf-8 -*-
"""從 DSH session 抽出對話中貼過的材料，存到 對話回覆/。"""
import compression.zstd as z
import hashlib
import io
import json
import os
import re

S = r'C:\Users\lionc\.dsh\sessions\--C-Users-lionc-OneDrive-~684C~9762-XW-~4E09~5927~90E8--\session-70937903-4831-422e-817b-e34516d7f4eb\session.v4.jsonl.zstd'
OUT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\對話回覆'
os.makedirs(OUT, exist_ok=True)
KEYS = ('## H0', '## G0', '| 編號 | 判定', '【鈔文】', '【疏文】', '【記文】', '【律文】')
seen = set()
num = 0


def texts(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from texts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from texts(v)


with z.ZstdFile(S, 'rb') as f:
    for line in f:
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('type') not in ('agent/inbox/spliced', 'user/message', 'assistant/message'):
            continue
        data = d.get('data', {})
        for t in texts(data):
            if len(t) < 300:
                continue
            if not any(k in t for k in KEYS):
                continue
            h = hashlib.sha1(t.encode('utf-8')).hexdigest()[:12]
            if h in seen:
                continue
            seen.add(h)
            num += 1
            fn = os.path.join(OUT, 'msg_%04d_%s.md' % (num, h))
            head = '# 對話材料 #%04d\n\n- event: %s\n- seq: %s\n- time: %s\n\n---\n\n' % (num, d.get('type'), d.get('seq'), d.get('time'))
            io.open(fn, 'w', encoding='utf-8').write(head + t)
            print(fn, len(t))
print('total', num)
