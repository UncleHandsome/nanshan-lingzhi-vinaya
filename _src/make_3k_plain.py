# -*- coding: utf-8 -*-
"""重建簡短版材料：每檔約 3KB，依書序、不按長度排序，不含分段指示。"""
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '六書_3K_20261124')
HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return len(HAN.findall(s or ''))


BOOKS = [
    ('xingshichao', '01_行事鈔', '行事鈔'),
    ('jieshu', '02_戒本疏行宗記', '戒本疏行宗記'),
    ('yeshu', '03_業疏', '業疏'),
    ('nicao', '04_尼鈔', '尼鈔'),
    ('yichao', '05_義鈔', '義鈔'),
    ('zhichi', '06_資持記', '資持記'),
]
PROMPT_FILE = os.path.join(B, '_src', 'review_prompt_universal.md')
PROMPT = io.open(PROMPT_FILE, encoding='utf-8').read().strip() + '\n'


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
        items = []
        for ln in io.open(os.path.join(B, '定稿', book_id + '.jsonl'), encoding='utf-8'):
            if not ln.strip():
                continue
            r = json.loads(ln)
            segs = r.get('segments') or []
            for si, s in enumerate(segs, 1):
                key = str(r['key']) if len(segs) == 1 else '%s-%d' % (r['key'], si)
                items.append((han(s.get('source') or ''), key, s))
        items.sort(key=lambda x: -x[0])  # 原文段落由長到短
        buf = []
        size = 0

        def flush():
            nonlocal buf, size, idx
            if not buf:
                return
            idx += 1
            body = (PROMPT.replace('{book_id}', book_id) + '\n\n'
                    + '\n'.join(buf))
            io.open(os.path.join(OUT, '%04d_%s.md' % (idx, book_id)), 'w',
                    encoding='utf-8', newline='\n').write(body)
            buf = []
            size = 0

        for _, key, s in items:
            b = block(book_id, label, key, s)
            n = len(b.encode('utf-8')) + 1
            if buf and size + n > 3000:
                flush()
            buf.append(b)
            size += n
        flush()
    print('files', idx, 'OUT', OUT)

if __name__ == '__main__':
    main()
