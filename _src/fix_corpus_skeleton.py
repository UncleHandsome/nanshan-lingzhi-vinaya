# -*- coding: utf-8 -*-
"""修復上游句讀語料的 punctuation 骨架區：用 TXT_句讀（ genuine）对应區段置換。

目標：
  TXT_句讀校定/yeshu.txt
  TXT_分卷_標點/03_業疏/*.txt（含骨架者）
參照：
  TXT_句讀/03_業疏/*.txt（依檔名順序接合）

只置換骨架區；前後以 12 漢字錨點對齊，確保漢字序列連續。
"""
import argparse
import glob
import io
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HAN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002f800-\U0002fa1f\uf900-\ufaff]')
NON = re.compile(r'[\sA-Za-z0-9]+')
LABEL = re.compile(r'【(?:疏|記|鈔|律|註|序)(?:文|序)?】')


def han(s):
    return ''.join(HAN.findall(s or ''))


def hindex(t):
    skip = set()
    for m in LABEL.finditer(t):
        skip.update(range(m.start(), m.end()))
    chars = []
    idx = []
    for i, ch in enumerate(t):
        if i in skip:
            continue
        if HAN.match(ch):
            chars.append(ch)
            idx.append(i)
    return ''.join(chars), idx


def density(s):
    nw = NON.sub('', s)
    return len(han(s)) / len(nw) if nw else 1.0


def skeleton_regions(t):
    h, idx = hindex(t)
    mark = [False] * len(h)
    for j in range(len(h)):
        a = idx[max(0, j - 25)]
        b = idx[min(len(h) - 1, j + 25)] + 1
        if density(t[a:b]) < 0.3:
            mark[j] = True
    regions = []
    j = 0
    while j < len(h):
        if mark[j]:
            k = j
            while k + 1 < len(h) and mark[k + 1]:
                k += 1
            if k - j >= 3:
                regions.append((j, k))
            j = k + 1
        else:
            j += 1
    return regions, h, idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    gfiles = sorted(glob.glob(os.path.join(B, 'TXT_句讀', '03_業疏', '*.txt')))
    HEADER = re.compile(r'^四分律刪補隨機羯磨疏\u3000卷[^\n]*\n（句讀版）\n=+\n')
    gtext = '\n'.join(HEADER.sub('', io.open(f, encoding='utf-8').read()) for f in gfiles)
    gh, gidx = hindex(gtext)
    targets = [os.path.join(B, 'TXT_句讀校定', 'yeshu.txt')]
    targets += sorted(glob.glob(os.path.join(B, 'TXT_分卷_標點', '03_業疏', '*.txt')))
    for p in targets:
        t = io.open(p, encoding='utf-8').read()
        regions, h, idx = skeleton_regions(t)
        if not regions:
            continue
        print('\n', os.path.relpath(p, B), 'regions', len(regions), flush=True)
        repl = []
        cursor = 0
        for J1, J2 in regions:
            if J1 < 12 or J2 + 13 > len(h):
                print('  edge region skip', J1, J2)
                repl.append(None)
                continue
            pre = h[J1 - 12:J1]
            suf = h[J2 + 1:J2 + 13]
            gp = gh.find(pre, cursor)
            if gp < 0:
                gp = gh.find(pre)
            if gp < 0:
                print('  pre not found', repr(pre))
                repl.append(None)
                continue
            g_end = gp + len(pre)
            gq = gh.find(suf, g_end, g_end + 4000)
            if gq < 0:
                gq = gh.find(suf, g_end)
            if gq < 0:
                print('  suf not found', repr(suf))
                repl.append(None)
                continue
            cursor = gq + len(suf)
            ta = idx[J1 - 1] + 1
            tb = idx[J2 + 1]
            ga = gidx[g_end - 1] + 1
            gb = gidx[gq]
            replacement = gtext[ga:gb]
            repl.append((ta, tb, replacement))
            print('  [%d:%d] han %d->%d %s' % (J1, J2, J2 - J1 + 1, len(han(replacement)), repr(replacement[:45])), flush=True)
        if a.apply:
            shutil.copy2(p, p + '.bak_skeleton_20261124')
            new = t
            for item in reversed(repl):
                if item:
                    ta, tb, replacement = item
                    new = new[:ta] + replacement + new[tb:]
            io.open(p, 'w', encoding='utf-8', newline='\n').write(new)
            left, _, _ = skeleton_regions(new)
            print('  saved; remaining regions', len(left), flush=True)


if __name__ == '__main__':
    main()
