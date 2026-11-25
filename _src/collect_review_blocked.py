# -*- coding: utf-8 -*-
"""把審閱批次被「內容審查」(DataInspection) 擋掉的檔案收集到一個資料夾。

輸出：
  審查擋檔_20261125/<stem>.md      被擋的材料原檔（可直接重跑）
  審查擋檔_20261125/清單.csv       檔名、書、大小、時間、錯誤碼
  審查擋檔_20261125/_其他失敗.txt  非審查類失敗（網路/JSON 等）
可重複執行：每次都重新掃 progress.jsonl 並補齊。
"""
import io
import json
import os
import glob
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RUN = os.path.join(B, '六書_3K_跑_20261124')
MAT = os.path.join(B, '六書_3K_20261124')
OUT = os.path.join(B, '審查擋檔_20261125')


def main():
    os.makedirs(OUT, exist_ok=True)
    prog = os.path.join(RUN, 'progress.jsonl')
    if not os.path.exists(prog):
        print('no progress.jsonl')
        return
    blocked = {}
    other = {}
    for ln in io.open(prog, encoding='utf-8'):
        if not ln.strip():
            continue
        o = json.loads(ln)
        st = o.get('status') or ''
        if not st.startswith('fail'):
            continue
        stem = o.get('file')
        if not o.get('t_start'):      # 昨晚那批（舊格式，無 t_start）不收
            continue
        blocked.setdefault(stem, o)
    n = 0
    done = 0
    keep = set()
    rows = ['file,book,KB,t_start,dur_s,error']
    for stem, o in sorted(blocked.items()):
        src = os.path.join(MAT, stem + '.md')
        if not os.path.exists(src):
            continue
        rep = os.path.join(RUN, '輸出', stem + '_回.txt')
        if os.path.exists(rep) and os.path.getsize(rep) > 0:
            done += 1
            continue
        shutil.copyfile(src, os.path.join(OUT, stem + '.md'))
        keep.add(stem + '.md')
        n += 1
        book = stem.rsplit('_', 1)[-1]
        rows.append('%s,%s,%d,%s,%s,%s' % (
            stem, book, os.path.getsize(src) // 1024, o.get('t_start', ''),
            o.get('dur_s', ''), (o.get('status') or '').split(':', 1)[-1].strip().strip('"')[:60]))
    io.open(os.path.join(OUT, '清單.csv'), 'w', encoding='utf-8-sig', newline='\n').write('\n'.join(rows) + '\n')
    for f in glob.glob(os.path.join(OUT, '*.md')):
        if os.path.basename(f) not in keep:
            os.remove(f)
    print('審查擋檔 %d 個（已補回覆、略過 %d）→ %s' % (n, done, OUT))


if __name__ == '__main__':
    main()
