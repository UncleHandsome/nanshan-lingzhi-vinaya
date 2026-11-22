# -*- coding: utf-8 -*-
"""補產缺少的長段審核包（每包 5 段）。"""
import io
import os
import re
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import mk_audit_materials as A  # noqa: E402

SRC = os.path.join(B, '測試', '重譯', '行事鈔', '_長段', '_終審')
OUT = os.path.join(B, '測試', '長段審核包_補')
MISS = ['04a_卷上之四_L0023', '04b_卷上之四_L0006', '04b_卷上之四_L0008',
        '04b_卷上之四_L0011', '06b_卷中之二_L0010', '06b_卷中之二_L0024',
        '06b_卷中之二_L0029', '06c_卷中之二_L0003', '06c_卷中之二_L0006',
        '06c_卷中之二_L0009', '06c_卷中之二_L0018', '07a_卷中之三_L0002',
        '07a_卷中之三_L0004']


def parse(t):
    i = t.index('\n【原文】\n')
    j = t.index('\n【待審譯文】\n')
    k = t.find('\n【後文背景', j)
    return t[i + 5:j].strip(), t[j + 9:k if k > 0 else len(t)].strip()


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    base = A.render_audit('《行事鈔》為比丘律制，部別稱謂須與比丘眾相應')
    head = base + '''

### 本次為長段批次（每包 5 段）
請逐段審核，**每段必須先單獨輸出完整檔名**，再做該段的【逐句簡核】【結論】【必改硬傷】。
格式：
```
【檔名】<該段完整檔名>
【逐句簡核】……
【結論】PASS 或 FIX
【必改硬傷】……（PASS 時只寫「無」）
```
嚴禁只寫編號、嚴禁把多段合併成一份結論。
'''
    n = 0
    for i in range(0, len(MISS), 5):
        grp = MISS[i:i + 5]
        L = [head, '', '---', '']
        for n2, k in enumerate(grp, 1):
            t = io.open(os.path.join(SRC, k + '.md'), encoding='utf-8').read()
            orig, tr = parse(t)
            L += ['## 第 %d 段' % n2, '', '（檔名：%s）' % k, '',
                  '【原文】', '', orig, '', '【待審譯文】', '', tr, '']
        n += 1
        io.open(os.path.join(OUT, 'fix%02d_%s.md' % (n, grp[0])), 'w',
                encoding='utf-8').write('\n'.join(L) + '\n')
    print('已產生 %d 包（%d 段）→ %s' % (n, len(MISS), OUT))


if __name__ == '__main__':
    main()
