# -*- coding: utf-8 -*-
"""重建簡短版材料：每檔約 3KB，依書序、不按長度排序，不含分段指示。"""
import io
import json
import os
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '六書_3K_20261124')
BOOKS = [
    ('xingshichao', '01_行事鈔', '行事鈔'),
    ('jieshu', '02_戒本疏行宗記', '戒本疏行宗記'),
    ('yeshu', '03_業疏', '業疏'),
    ('nicao', '04_尼鈔', '尼鈔'),
    ('yichao', '05_義鈔', '義鈔'),
    ('zhichi', '06_資持記', '資持記'),
]
PROMPT = '''<!--
Qwen 校閱指示：
逐段檢查下面各段「白話」有沒有問題。只回報有問題的段，不要重寫沒問題的段。
- 有問題：輸出該段修正後完整白話。
- 沒問題：不要輸出。
- 只輸出 JSONL，每行一個物件：{{"book_id":"{book_id}","key":"...","translation":"..."}}
- key 只填 ## 後面斜線後的代號，不要包含書名。
- 不要 code fence、前言、解釋，也不要改原文或 key。
- 整檔全部沒問題，只回覆：NONE
-->
'''


def block(book_id, book_label, key, s):
    lab = s.get('label') or '疏文'
    src = (s.get('display_source') or s.get('source') or '').strip()
    tr = (s.get('translation') or '').strip()
    return '\n'.join([
        '## %s／%s' % (book_label, key), '',
        '### 原文', '', '【%s】' % lab, src, '',
        '### 白話', '', '【%s】' % lab, tr, '',
    ])


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    idx = 0
    for book_id, _, label in BOOKS:
        buf = []; size = 0
        def flush():
            nonlocal buf, size, idx
            if not buf:
                return
            idx += 1
            body = (PROMPT.format(book_id=book_id) + '\n\n'
                    + '\n'.join(buf))
            io.open(os.path.join(OUT, '%04d_%s.md' % (idx, book_id)), 'w',
                    encoding='utf-8', newline='\n').write(body)
            buf = []; size = 0
        for ln in io.open(os.path.join(B, '定稿', book_id + '.jsonl'), encoding='utf-8'):
            if not ln.strip():
                continue
            r = json.loads(ln)
            segs = r.get('segments') or []
            for si, s in enumerate(segs, 1):
                key = str(r['key']) if len(segs) == 1 else '%s-%d' % (r['key'], si)
                b = block(book_id, label, key, s)
                n = len(b.encode('utf-8')) + 1
                if buf and size + n > 3000:
                    flush()
                buf.append(b); size += n
        flush()
    print('files', idx, 'OUT', OUT)


if __name__ == '__main__':
    main()
