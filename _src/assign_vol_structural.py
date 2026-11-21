# -*- coding: utf-8 -*-
"""vol/chunk 只依 raw 卷題位置分配，不看 key、不看舊頁、不做鄰居補。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {
 'xingshichao': ('TXT/01_四分律刪繁補闕行事鈔.txt', r'【四分律刪繁補闕行事鈔(卷[上中下](?:之[一二三四])?)】'),
 'yeshu': ('TXT/03_四分律刪補隨機羯磨疏.txt', r'【四分律刪補隨機羯磨疏(?:濟緣記)?(卷[一二三四](?:之[一二三四])?)】'),
 'nicao': ('TXT/04_四分律比丘尼鈔.txt', r'【四分律比丘尼鈔(卷[上中下](?:之[上中下])?)】'),
 'yichao': ('TXT/05_四分律拾毗尼義鈔.txt', r'【四分律拾毗尼義鈔(卷[上中下](?:之[一二三四])?)】'),
}
def norm(v):
    m = re.match(r'卷([上中下]|[一二三四])', v)
    return '卷' + m.group(1) if m else v
for book, (rawp, pat) in BOOKS.items():
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
    marks = [(m.start(), m.group(1)) for m in re.finditer(pat, raw)]
    if not marks:
        print(book, 'NO MARKS'); continue
    p = os.path.join(B, '定稿', book + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    for r in rows:
        q = r.get('raw_start', -1)
        if q >= 0:
            last = None
            for pos, txt in marks:
                if pos <= q:
                    last = (pos, txt)
                else:
                    break
            if last:
                r['chunk'] = last[1]
                r['vol'] = norm(last[1])
            else:
                r['chunk'] = '卷首'
                r['vol'] = norm(marks[0][1])
        else:
            r['vol'] = '未定位'; r['chunk'] = '未定位'
    io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    print(book, {v: sum(1 for r in rows if r['vol'] == v) for v in ['卷上','卷中','卷下','卷一','卷二','卷三','卷四','未定位'] if any(r['vol']==v for r in rows)})
