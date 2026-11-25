# -*- coding: utf-8 -*-
"""修復：把回覆檔裡「key 不屬於該檔」的行清掉（GAP44-5 曾被誤剝成 GAP44）。

1. 讀 六書_3K_20261124/<stem>.md 的標題 key（完整比對）
2. 逐行檢查 六書_3K_跑_20261124/輸出/<stem>_回.txt
   若該行是 JSON 且其 key 不在該檔標題 key 內 → 刪該行
3. 若刪完沒有任何 JSON 物件（原本有）→ 整個檔刪除（之後可重匯）
"""
import glob
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '六書_3K_20261124')
RAW = os.path.join(B, '六書_3K_跑_20261124', '輸出')
HEAD_RE = re.compile(r'^##\s+([^／\n]+)／(.+?)\s*$', re.M)


def main():
    head = {}
    for p in glob.glob(os.path.join(MAT, '*.md')):
        stem = os.path.basename(p)[:-3]
        head[stem] = {m.group(2).strip() for m in HEAD_RE.finditer(io.open(p, encoding='utf-8').read())}
    fixed_files = dropped_lines = removed_files = 0
    for p in sorted(glob.glob(os.path.join(RAW, '*_回.txt'))):
        stem = os.path.basename(p)[:-6]
        keys = head.get(stem)
        if keys is None:
            continue
        lines = io.open(p, encoding='utf-8').read().split('\n')
        keep = []
        drop = 0
        had_json = False
        kept_json = 0
        for ln in lines:
            s = ln.strip()
            if not s.startswith('{'):
                keep.append(ln)
                continue
            try:
                o = json.loads(s)
            except Exception:
                keep.append(ln)
                continue
            if not isinstance(o, dict) or 'key' not in o:
                keep.append(ln)
                continue
            had_json = True
            if str(o.get('key')).strip() in keys:
                keep.append(ln)
                kept_json += 1
            else:
                drop += 1
        if drop:
            fixed_files += 1
            dropped_lines += drop
            if had_json and kept_json == 0:
                os.remove(p)
                removed_files += 1
                print('  刪檔 %s（%d 行全不屬此檔）' % (stem, drop))
            else:
                io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(keep))
                print('  清行 %s（刪 %d）' % (stem, drop))
    print('處理檔案 %d，刪行 %d，刪檔 %d' % (fixed_files, dropped_lines, removed_files))


if __name__ == '__main__':
    main()
