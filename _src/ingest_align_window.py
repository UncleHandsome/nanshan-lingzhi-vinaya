# -*- coding: utf-8 -*-
"""把外部 AI 跑回來的「整窗對位」JSONL 寫成對位結果檔。

用法：
  python -X utf8 _src/ingest_align_window.py 你的輸出.txt pian17_二衣總別_part01 [--dry]

輸出：對位結果_20261125/<窗名>.jsonl
  - 依該窗 _windows.json 的記段順序輸出，缺的記段補 orphan
  - A 只保留該窗（或該篇）真正存在的鈔段 key
  - 接受 {"B":...,"A":[...],"type":...} 或 {"key":...,"A":[...],"note":...}
"""
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '對位材料_20261125')
RES = os.path.join(B, '定稿', '對位結果_20261125')


def norm(x):
    return re.sub(r'^(記|鈔|記段|鈔段)\s*', '', str(x or '').strip()).strip('[]「」')


def main():
    if len(sys.argv) < 3:
        print('usage: ingest_align_window.py <out.txt> <window_stem> [--dry]')
        return
    src, stem = sys.argv[1], sys.argv[2]
    dry = '--dry' in sys.argv
    wins = {w['file'][:-3]: w for w in
            json.load(io.open(os.path.join(MAT, '_windows.json'), encoding='utf-8'))}
    win = wins.get(stem) or wins.get(stem + '.md')
    if not win:
        print('找不到窗：', stem, '（可用：%s）' % ', '.join(sorted(wins)[:5]))
        return
    ji = win['ji_keys']
    chao = set(win['chao_keys'])
    objs = {}
    for ln in io.open(src, encoding='utf-8'):
        s = ln.strip()
        if s.startswith('```') or not s.startswith('{'):
            continue
        try:
            o = json.loads(s)
        except Exception:
            continue
        k = norm(o.get('B') or o.get('key'))
        if k:
            objs[k] = o
    lines = []
    miss = 0
    for k in ji:
        o = objs.get(k)
        if not o:
            miss += 1
            lines.append({'B': k, 'A': [], 'type': 'orphan', 'why': '未輸出'})
            continue
        a = [norm(x) for x in (o.get('A') or [])]
        a = [x for x in a if x in chao]
        t = str(o.get('type') or '').strip()
        lines.append({'B': k, 'A': a,
                      'type': t or ('orphan' if not a else ('1:1' if len(a) == 1 else '1:n')),
                      'why': str(o.get('note') or o.get('why') or '')[:200]})
    orph = sum(1 for x in lines if not x['A'])
    print('%s：窗內記段 %d，收到 %d，缺 %d，orphan %d' % (stem, len(ji), len(objs), miss, orph))
    if dry:
        return
    dst = os.path.join(RES, stem + '.jsonl')
    io.open(dst, 'w', encoding='utf-8', newline='\n').write(
        '\n'.join(json.dumps(x, ensure_ascii=False) for x in lines) + '\n')
    print('寫入', dst)


if __name__ == '__main__':
    main()
