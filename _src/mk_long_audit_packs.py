# -*- coding: utf-8 -*-
"""把長段每 5 段合成一份審核包（含現行 AUDIT_PROMPT，要求輸出完整檔名）。"""
import io
import os
import re
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import mk_audit_materials as A  # noqa: E402

SRC = os.path.join(B, '測試', '重譯', '行事鈔', '_長段', '_終審')
OUT = os.path.join(B, '測試', '長段審核包')


def parse(t):
    i = t.find('【原文】')
    j = t.find('【待審譯文】')
    k = t.find('【後文背景', j)
    orig = t[i + len('【原文】'):j].strip()
    tr = t[j + len('【待審譯文】'):k if k > 0 else len(t)].strip()
    return orig, tr


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    keys = sorted(f[:-3] for f in os.listdir(SRC) if f.endswith('.md'))
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

嚴禁只寫編號、嚴禁把多段合併成一份結論；每段都要有完整檔名。
'''
    n = 0
    for i in range(0, len(keys), 5):
        grp = keys[i:i + 5]
        L = [head, '', '---', '']
        for n2, k in enumerate(grp, 1):
            t = io.open(os.path.join(SRC, k + '.md'), encoding='utf-8').read()
            orig, tr = parse(t)
            L += ['## 第 %d 段' % n2, '', '（檔名：%s）' % k, '',
                  '【原文】', '', orig, '', '【待審譯文】', '', tr, '']
        n += 1
        fn = 'pack%02d_%s.md' % (n, grp[0])
        io.open(os.path.join(OUT, fn), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('已產生 %d 個審核包（每包 5 段，共 %d 段）→ %s' % (n, len(keys), OUT))


if __name__ == '__main__':
    main()
