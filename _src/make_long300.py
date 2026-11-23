# -*- coding: utf-8 -*-
"""準備單一段落 >300 漢字的 Qwen 拆分材料。"""
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '單段300_待拆')
BOOKS = [
    ('xingshichao', '行事鈔'),
    ('jieshu', '戒本疏行宗記'),
    ('yeshu', '業疏'),
    ('nicao', '尼鈔'),
    ('yichao', '義鈔'),
    ('zhichi', '資持記'),
]
HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return len(HAN.findall(s or ''))


def main():
    items = []
    for order, (bid, label) in enumerate(BOOKS):
        for ln in io.open(os.path.join(B, '定稿', bid + '.jsonl'), encoding='utf-8'):
            if not ln.strip():
                continue
            r = json.loads(ln)
            for i, s in enumerate(r.get('segments') or []):
                n = han(s.get('source') or '')
                if n <= 300:
                    continue
                items.append({
                    'book_id': bid, 'book': label, 'key': str(r['key']),
                    'seg': i + 1, 'label': s.get('label') or '疏文',
                    'src': s.get('display_source') or s.get('source') or '',
                    'tr': s.get('translation') or '', 'chars': n, 'order': order,
                })
    items.sort(key=lambda x: (-x['chars'], x['order'], x['key'], x['seg']))
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for i, x in enumerate(items, 1):
        prompt = '''<!--
Qwen 校閱指示：
請把下面這一個 segment 的原文與白話依語意自然分段。
- 原文只輸出每段的開頭 head（12–20 字），不必重抄整段原文。
- head 必須在該 segment 原文中唯一出現；第一個 head 必須是原文開頭。
- 每段輸出對應的完整白話 translation。
- 只輸出一個 JSON，不要 code fence、前言或解釋：
  {"book_id":"%s","key":"%s","segment":%d,"parts":[{"head":"原文第一段開頭","translation":"白話第一段"},{"head":"原文第二段開頭","translation":"白話第二段"}]}
- parts 必須依序覆蓋該 segment 全部原文。
-->
''' % (x['book_id'], x['key'], x['seg'])
        body = '\n'.join([
            '# 單段拆分　%04d' % i, '',
            '本段原文 %d 字。' % x['chars'], '',
            prompt, '',
            '## %s／%s（book_id=%s，segment=%d）' % (x['book'], x['key'], x['book_id'], x['seg']),
            '',
            '### 原文', '', '【%s】' % x['label'], x['src'], '',
            '### 白話', '', '【%s】' % x['label'], x['tr'], '',
        ])
        io.open(os.path.join(OUT, '%04d_%s_%s_s%d.md' % (i, x['book_id'], re.sub(r'[^\w\u4e00-\u9fff-]', '_', x['key']), x['seg'])),
                'w', encoding='utf-8', newline='\n').write(body)
    io.open(os.path.join(OUT, '_order.json'), 'w', encoding='utf-8').write(
        json.dumps([{k: x[k] for k in ('book_id', 'key', 'seg', 'label', 'chars')} for x in items],
                   ensure_ascii=False, indent=1) + '\n')
    print('files', len(items), 'OUT', OUT)


if __name__ == '__main__':
    main()
