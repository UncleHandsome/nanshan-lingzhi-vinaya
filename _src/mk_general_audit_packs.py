# -*- coding: utf-8 -*-
"""行事鈔一般段「審核包」：每包原文約 2,956 字，提示詞只放一次，
中間組省略前後背景，並要求每組先輸出完整檔名。"""
import io
import os
import re
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import mk_audit_materials as A  # noqa: E402

SRC = os.path.join(B, '測試', '重譯', '行事鈔', '_終審')
OUT = os.path.join(B, '測試', '行事鈔審核包')
TARGET = 2956
H = re.compile(r'[\u4e00-\u9fff]')


def split_mat(t):
    pre = post = ''
    m = re.search(r'【前文背景（僅供參考[^】]*）】\s*\n+(.+?)(?=\n+【|\Z)', t, re.S)
    if m:
        pre = m.group(1).strip()
    i = t.index('\n【原文】\n')
    j = t.index('\n【待審譯文】\n')
    k = t.find('\n【後文背景', j)
    m2 = re.search(r'【後文背景（僅供參考[^】]*）】\s*\n+(.+?)(?=\Z)', t, re.S)
    if m2:
        post = m2.group(1).strip()
    return pre, t[i + 5:j].strip(), t[j + 9:k if k > 0 else len(t)].strip(), post


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    keys = sorted(f[:-3] for f in os.listdir(SRC) if f.endswith('.md'))
    items = []
    for k in keys:
        t = io.open(os.path.join(SRC, k + '.md'), encoding='utf-8').read()
        pre, orig, tr, post = split_mat(t)
        items.append({'key': k, 'pre': pre, 'orig': orig, 'tr': tr,
                      'post': post, 'n': len(H.findall(orig))})
    packs, cur, n = [], [], 0
    for it in items:
        if cur and (n + it['n'] > TARGET or len(cur) >= 30):
            packs.append(cur)
            cur, n = [], 0
        cur.append(it)
        n += it['n']
    if cur:
        packs.append(cur)
    base = A.render_audit('《行事鈔》為比丘律制，部別稱謂須與比丘眾相應')
    head = base + '''

### 本次為打包批次（每包約 28 組）
請逐組審核，**每組必須先單獨輸出完整檔名**，再做該組的【逐句簡核】【結論】【必改硬傷】。
格式：
```
【檔名】<該組完整檔名>
【逐句簡核】……
【結論】PASS 或 FIX
【必改硬傷】……（PASS 時只寫「無」）
```
嚴禁只寫編號、嚴禁把多組合併成一份結論。
'''
    for i, pack in enumerate(packs, 1):
        L = [head, '', '---', '', '（本包共 %d 組，依原順序排列）' % len(pack), '']
        if pack[0]['pre']:
            L += ['【前文背景（僅供參考）】', '', pack[0]['pre'], '']
        for j, it in enumerate(pack, 1):
            L += ['## 第 %d 組｜%s' % (j, it['key']), '',
                  '【原文】', '', it['orig'], '', '【待審譯文】', '', it['tr'], '']
        if pack[-1]['post']:
            L += ['【後文背景（僅供參考）】', '', pack[-1]['post'], '']
        io.open(os.path.join(OUT, 'audit%03d_%s.md' % (i, pack[0]['key'])), 'w',
                encoding='utf-8').write('\n'.join(L) + '\n')
    tot = sum(len(H.findall(io.open(os.path.join(OUT, f), encoding='utf-8').read()))
              for f in os.listdir(OUT))
    print('已產生 %d 個審核包（%d 組），平均 %d 字／包'
          % (len(packs), len(items), round(tot / len(packs))))


if __name__ == '__main__':
    main()
