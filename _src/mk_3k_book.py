# -*- coding: utf-8 -*-
"""用內部 JSONL 提示詞，重新產生單一書的 3K 審閱材料（每檔約 3K 字）。

用法：
  python -X utf8 _src/mk_3k_book.py --book xingshichao --out 重審_行事鈔_3K_20261126

每檔：提示詞（_src/review_prompt_universal.md）＋若干段
  ## 行事鈔／key
  ### 原文 … ### 白話 …
以「原文漢字數」累計，達 --limit（預設 350）即換檔。
"""
import argparse
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HAN = re.compile(r'[\u4e00-\u9fff]')
PROMPT_FILE = os.path.join(B, '_src', 'review_prompt_universal.md')
LABELS = {'xingshichao': '行事鈔', 'jieshu': '戒本疏行宗記', 'yeshu': '業疏',
          'nicao': '尼鈔', 'yichao': '義鈔', 'zhichi': '資持記'}


def han(s):
    return len(HAN.findall(s or ''))


LBL_RE = re.compile(r'^\s*(?:【(?:疏文|記文|鈔文|律文|註文|序文)】\s*)+')


def block(book_label, key, s):
    lab = s.get('label') or '疏文'
    src = LBL_RE.sub('', (s.get('display_source') or s.get('source') or '').strip())
    tr = LBL_RE.sub('', (s.get('translation') or '').strip())
    return '\n'.join([
        '## %s／%s' % (book_label, key), '',
        '### 原文', '', '【%s】' % lab, src, '',
        '### 白話', '', '【%s】' % lab, tr, '',
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', default='xingshichao')
    ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=int, default=350)
    a = ap.parse_args()
    book_label = LABELS[a.book]
    prompt = io.open(PROMPT_FILE, encoding='utf-8').read().strip() + '\n'
    out = os.path.join(B, a.out)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith('.md'):
            os.remove(os.path.join(out, f))

    items = []
    for ln in io.open(os.path.join(B, '定稿', a.book + '.jsonl'), encoding='utf-8'):
        if not ln.strip():
            continue
        r = json.loads(ln)
        segs = r.get('segments') or []
        unit = []
        for si, s in enumerate(segs, 1):
            key = str(r['key']) if len(segs) == 1 else '%s-%d' % (r['key'], si)
            unit.append((key, s))
        if unit:
            items.append((int(r.get('raw_start') or 0), unit))
    items.sort(key=lambda x: (x[0], x[1]))

    idx = 0
    buf, size = [], 0
    total_keys = 0

    def flush():
        nonlocal buf, size, idx
        if not buf:
            return
        idx += 1
        body = prompt + '\n' + '\n'.join(buf)
        io.open(os.path.join(out, '%04d_%s.md' % (idx, a.book)), 'w',
                encoding='utf-8', newline='\n').write(body)
        buf, size = [], 0

    for _pos, unit in items:
        for key, s in unit:
            b = block(book_label, key, s)
            n = han(s.get('source') or '')
            if buf and size + n > a.limit:
                flush()
            buf.append(b)
            size += n
            total_keys += 1
    flush()
    print('book', a.book, 'keys', total_keys, 'files', idx, '->', out)


if __name__ == '__main__':
    main()
