# -*- coding: utf-8 -*-
"""保護既有成果並只產出「尚未建組」的補譯材料。"""
import io
import json
import os
import re
import shutil
import sys
import time

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, '測試')
sys.path.insert(0, os.path.join(B, '_src'))
import mk_review_materials as M  # noqa: E402

STAMP = time.strftime('%Y%m%d_%H%M%S')
BOOKS = ['業疏', '戒疏', '尼鈔', '行事鈔', '義鈔', '資持記']
PROV = re.compile(r'（出處：(?:《[^》]+》)?([^，]+)，第 (\d+)(?:–(\d+))? 段')


def backup(bk):
    root = os.path.join(T, '重譯', bk)
    for sub in ('_材料', '_盲翻_對齊', '_盲翻'):
        src = os.path.join(root, sub)
        if not os.path.isdir(src):
            continue
        if sub == '_材料':
            n = len([f for f in os.listdir(src) if f.endswith(('.md', '.json'))])
        else:
            d = os.path.join(src, '回覆')
            n = len([f for f in os.listdir(d) if f.endswith('_回.txt')]) if os.path.isdir(d) else 0
        dst = os.path.join(root, '_備份_%s_%s' % (sub.strip('_'), STAMP))
        if n == 0 or os.path.isdir(dst):
            continue
        shutil.copytree(src, dst)
        print('  備份 %s/%s：%d 檔' % (bk, sub, n))


def existing(bk):
    d = os.path.join(T, '重譯', bk, '_材料')
    spans = set()
    starts = set()
    if not os.path.isdir(d):
        return spans, starts
    for f in os.listdir(d):
        if not f.endswith('.md'):
            continue
        t = io.open(os.path.join(d, f), encoding='utf-8').read()
        m = PROV.search(t)
        if not m:
            continue
        ch = m.group(1).strip()
        a = int(m.group(2)) - 1
        b = int(m.group(3)) if m.group(3) else a + 1
        spans.add((ch, a, b))
        starts.add((ch, a))
    return spans, starts


def main():
    for bk in BOOKS:
        root = os.path.join(T, '重譯', bk)
        if not os.path.isdir(root):
            continue
        print('== %s ==' % bk)
        backup(bk)
        spans, starts = existing(bk)
        groups = M.build_groups(M.BOOKS[bk])
        todo = []
        for g in groups:
            key = (g['chunk'], g['s0'], g['g1'])
            if key in spans or (g['chunk'], g['s0']) in starts:
                continue
            todo.append(g)
        out = os.path.join(root, '_材料_補')
        if os.path.isdir(out):
            shutil.rmtree(out)
        os.makedirs(out, exist_ok=True)
        for i, g in enumerate(todo, 1):
            try:
                M.emit(g, 6, 4, out, i, book=bk)
            except Exception as e:
                print('   ⚠', g['chunk'], g['s0'], e)
        print('  既有 %d 組｜總組 %d｜待補 %d' % (len(spans), len(groups), len(todo)))


if __name__ == '__main__':
    main()
