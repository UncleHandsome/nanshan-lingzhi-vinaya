# -*- coding: utf-8 -*-
"""從目前定稿重產長段材料：只收尚未安全處理的 key。

舊批次 materials 是在 >300 切分前產生；這裡先算出：
- 舊回覆 NONE：視為已看過
- 舊回覆 parts 且能用目前定稿通過 head 驗證：已處理
- 其餘（未跑、parts 驗證失敗）：進新批次
"""
import glob
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OLD = os.path.join(B, '六書_500字_長段優先')
OUT = os.path.join(B, '六書_500字_長段_最終_20261124')
BOOKS = [
    ('xingshichao', '01_行事鈔', '行事鈔'),
    ('jieshu', '02_戒本疏行宗記', '戒本疏行宗記'),
    ('yeshu', '03_業疏', '業疏'),
    ('nicao', '04_尼鈔', '尼鈔'),
    ('yichao', '05_義鈔', '義鈔'),
    ('zhichi', '06_資持記', '資持記'),
]
HAN = re.compile(r'[\u4e00-\u9fff]')
HEAD = re.compile(r'^## .*?／([^（]+)（book_id=([a-z]+)）')


def han(s):
    return len(HAN.findall(s or ''))


def load_rows():
    rows = {}
    for bid, _, _ in BOOKS:
        for ln in io.open(os.path.join(B, '定稿', bid + '.jsonl'), encoding='utf-8'):
            if ln.strip():
                r = json.loads(ln); rows[(bid, str(r['key']))] = r
    return rows


def old_keys(path):
    out = []
    for ln in io.open(path, encoding='utf-8'):
        m = HEAD.match(ln.strip())
        if m:
            out.append((m.group(2), m.group(1)))
    return out


def main():
    rows = load_rows()
    reviewed = set(); bad = set()
    files = [p for p in glob.glob(os.path.join(OLD, '*.md')) if os.path.basename(p) != 'README.md']
    for p in files:
        keys = old_keys(p)
        if not keys:
            continue
        stem = os.path.basename(p)[:-3]
        rp = os.path.join(OLD, 'AI_output', stem + '_回.txt')
        # 舊 runner 的目錄名是 AI輸出（中文）；保留兩種
        if not os.path.exists(rp):
            rp = os.path.join(OLD, 'AI輸出', stem + '_回.txt')
        if not os.path.exists(rp):
            continue
        text = io.open(rp, encoding='utf-8').read().strip()
        if not text:
            continue
        if text.upper().rstrip('.。') == 'NONE':
            reviewed.update(keys); continue
        seen = set(); ok = True
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                o = json.loads(ln)
            except Exception:
                ok = False; break
            bid = o.get('book_id'); key = str(o.get('key') or '')
            if '／' in key: key = key.rsplit('／', 1)[-1]
            if '/' in key: key = key.rsplit('/', 1)[-1]
            seen.add((bid, key))
            r = rows.get((bid, key))
            if not r:
                ok = False; break
            # 用目前定稿驗證 parts 是否能安全切
            try:
                import sys
                sys.path.insert(0, os.path.join(B, '_src'))
                import apply_parts as A
                parts, err = A.parse_parts(o)
                new, info = A.split_row(r, parts) if parts else (None, err)
            except Exception:
                new = None
            if not new:
                ok = False
        if ok:
            reviewed.update(keys)
        else:
            bad.update(seen)
            # 同一檔其他沒出現在回覆的 key 視為無問題
            reviewed.update(k for k in keys if k not in seen)
    # 目標：所有目前 rows - reviewed + bad
    target = []
    for (bid, key), r in rows.items():
        if (bid, key) in bad or (bid, key) not in reviewed:
            target.append((bid, key, r))
    target.sort(key=lambda x: (-sum(han((s.get('source') or '')) for s in (x[2].get('segments') or [])), x[0], x[1]))
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    files_out = 0; buf = []; chars = 0; total = 0
    def flush():
        nonlocal buf, chars, files_out
        if not buf: return
        files_out += 1
        io.open(os.path.join(OUT, '%04d.md' % files_out), 'w', encoding='utf-8', newline='\n').write('\n'.join(buf))
        buf = []; chars = 0
    for bid, key, r in target:
        segs = r.get('segments') or []
        if not segs:
            continue
        n = sum(han((s.get('source') or '')) for s in segs)
        total += n
        if buf and chars + n > 550:
            flush()
        bname = next(x[2] for x in BOOKS if x[0] == bid)
        block = ['## %s／%s（book_id=%s）' % (bname, key, bid), '', '### 原文', '']
        for i, s in enumerate(segs, 1):
            block += ['【%d・%s】' % (i, s.get('label') or '疏文'), s.get('display_source') or s.get('source') or '', '']
        block += ['### 白話', '']
        for s in segs:
            block += ['【%s】' % (s.get('label') or '疏文'), s.get('translation') or '', '']
        buf.append('\n'.join(block)); chars += n
    flush()
    prompt = '''<!--
Qwen 校閱指示：
你是校閱者。請檢查下面各段白話文有沒有實質問題，只回報有問題的段，不要重寫沒問題的段。
- 原文已按 segment 編號：【1・疏文】【2・記文】…；不要改 segment 編號。
- 若這一行有問題：parts 必須覆蓋這一行全部 segments，從 1 到最後一個 segment，不可只回報有問題的那一個 segment。
- 每個 segment 內，分段由你決定；每個 part 輸出該段原文的開頭 head（12–20 字），不必重抄整段。
- head 必須在該 segment 原文中唯一出現；第一個 head 必須是該 segment 原文開頭。
- translation 對應從這個 head 到下一個 head 之前的原文；parts 必須覆蓋該 segment 全部原文。
- 短段可以只有一個 part，不要硬切。
- 只輸出 JSONL，每行一個物件：
  {"book_id":"...","key":"...","parts":[{"segment":1,"head":"...","translation":"..."}]}
- 整行沒問題就不輸出；整檔沒問題只回覆 NONE。
- 不要 code fence、前言或解釋。
-->
'''
    # 把 prompt 插到每個檔最前面
    for p in glob.glob(os.path.join(OUT, '*.md')):
        body = io.open(p, encoding='utf-8').read()
        io.open(p, 'w', encoding='utf-8', newline='\n').write(prompt + '\n' + body)
    print('target_rows', len(target), 'target_chars', total, 'files', files_out)
    print('reviewed', len(reviewed), 'bad', len(bad))
    print('OUT', OUT)


if __name__ == '__main__':
    main()
