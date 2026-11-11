# -*- coding: utf-8 -*-
"""Generate 存疑材料/complex_存疑/*.md + index.tsv."""
import json, os, re, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
DST = os.path.join(ROOT, '存疑材料', 'complex_存疑')

PROMPT = """你是南山律典譯文的資深校勘者。下面每條有一個「疑點」，是前一位校閱者不確定、暫時擱下的問題。

請對每一條給出明確結論，不要含糊：

1. 讀原文與譯文，判斷疑點成立不成立。
2. 結論只有三種：
   - 是錯：指出錯在哪，並給整段替換文字。
   - 不是錯：說明為什麼原文支持現行譯法。
   - 材料不足：指出缺什麼（例如需要查某部論、某卷律），不要猜。

輸出格式（每條一段）：

### 01-0014｜是錯｜P1
判斷：譯文把原文的兩本書併成一本，原文用頓號並列，應為二書。
建議：（整段替換文字，其餘與現譯逐字相同）

### 01-0052｜不是錯
判斷：原文「擇律師」為人名異寫，譯文作「法擇律師」有據，不構成錯誤。

### 01-0130｜材料不足
判斷：需查《十住毘婆沙論》是否為一書，現有材料無法判定。

規則：
- 「是錯」才給建議，且必須是完整段落。
- 不要為了有結論而硬判；材料不足就寫材料不足。
- 不要改原文、不要合併段落、不要加譯者按語。"""

def norm(x):
    return re.sub(r'\s+', '', x or '')

def main():
    items = json.load(open(os.path.join(OUT, 'items.json'), encoding='utf-8'))
    S = json.load(open(os.path.join(OUT, 'segidx.json'), encoding='utf-8'))
    codes, labels = S['codes'], S['labels']
    cur = json.load(open(os.path.join(OUT, 'cur.json'), encoding='utf-8'))
    # refresh paragraphs from disk (post-fix current text)
    disk = {}
    import glob
    for f in glob.glob(os.path.join(ROOT, 'AI語譯', 'out', '**', '*.txt'), recursive=True):
        book = os.path.basename(os.path.dirname(f))
        if book.startswith('_'):
            continue
        chunk = os.path.splitext(os.path.basename(f))[0]
        raw = open(f, 'rb').read().decode('utf-8')
        eol = '\r\n' if '\r\n' in raw else '\n'
        blocks = [b for b in re.split(re.escape(eol + eol), raw) if b.strip()]
        for n, b in enumerate(blocks, 1):
            disk['%s/%s#%d' % (book, chunk, n)] = b
    cur = disk

    doubt = [i for i in items if i['section'] == 'doubt']
    # drop section-header pseudo items
    doubt = [i for i in doubt if (i.get('問題') or '').strip()]
    # low-confidence findings
    find = [i for i in items if i['section'] == 'find']
    low = [i for i in find if (i.get('信心') or '').startswith('低')]
    pool = doubt + [dict(x, section='doubt') for x in low]

    rows = []
    seen = set()
    for it in pool:
        lab = (it.get('label') or '').strip()
        code = (it.get('code') or '').strip()
        if not lab and code and code in codes:
            lab = codes[code]['label']
        if not lab:
            m = re.search(r'([\u4e00-\u9fff]{2,4}_[^\s#：]+#\d+)', it.get('問題') or '')
            if m:
                lab = m.group(1)
        if not lab or lab not in cur:
            continue
        reason = re.sub(r'\s+', ' ', it.get('問題') or '').strip()
        key = (lab, norm(reason)[:40])
        if key in seen:
            continue
        seen.add(key)
        src = labels[lab]['src'] if lab in labels else ''
        rows.append({'code': code, 'label': lab, 'src': src, 'tr': cur[lab], 'reason': reason,
                     'conf': (it.get('信心') or '')[:1]})

    rows.sort(key=lambda r: (r['label'], r['code']))
    os.makedirs(DST, exist_ok=True)
    # split evenly so every file holds 8-12 entries
    import math
    n_total = len(rows)
    n_files = max(1, math.ceil(n_total / 12.0))
    base, rem = divmod(n_total, n_files)
    sizes = [base + (1 if i < rem else 0) for i in range(n_files)]
    assert all(8 <= s <= 12 for s in sizes), sizes
    index = []
    pos = 0
    for fi, size in enumerate(sizes, 1):
        chunk = rows[pos:pos + size]; pos += size
        fn = 'complex_%02d.md' % fi
        lines = ['# complex 批存疑材料 %02d（%d 條）' % (fi, len(chunk)), '']
        lines += ['> 來源：`batch_qwen/r1_complex/resp_*.txt`（校閱_10K 第 1–578 號中實送 549 檔）「存疑」條目與「信心：低」條目。', '']
        lines += ['## 裁判提示詞（全文，貼給裁判模型）', '', '```text', PROMPT, '```', '']
        lines += ['## 材料開始', '']
        for k, r in enumerate(chunk, 1):
            tag = r['code'] or ('%s-%02d' % (r['label'].split('/')[1].split('#')[0], k))
            lines.append('【存疑 %s】%s' % (tag, r['label']))
            lines.append('【原文】%s' % (r['src'] or '（材料缺）'))
            lines.append('【譯文】%s' % r['tr'])
            lines.append('【疑點】%s' % r['reason'])
            lines.append('')
        open(os.path.join(DST, fn), 'w', encoding='utf-8').write('\n'.join(lines))
        index.append((fn, len(chunk)))
    with open(os.path.join(DST, 'index.tsv'), 'w', encoding='utf-8') as f:
        f.write('檔名\t條數\n')
        for fn, c in index:
            f.write('%s\t%d\n' % (fn, c))
    print('entries', len(rows), 'files', len(index))
    print('by chunk:', collections.Counter(r['label'].split('#')[0] for r in rows).most_common(8))

if __name__ == '__main__':
    main()
