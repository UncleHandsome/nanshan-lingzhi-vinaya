# -*- coding: utf-8 -*-
"""對齊檢查：全量掃描每本書的材料與回覆，回報錯位比例與清單。

用法： python -X utf8 _src/check_align.py [--books 業疏,...] [--strict]
"""
import argparse
import io
import os
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, '測試')
sys.path.insert(0, os.path.join(B, '_src'))
import materials_io as MI  # noqa: E402

SUF = '_回.txt'
MIN_SAME = 0.06


def grams(t, n=3):
    s = ''.join(ch for ch in t if '\u4e00' <= ch <= '\u9fff')
    return set(s[i:i + n] for i in range(0, max(0, len(s) - n + 1)))


def ov(a, b):
    return len(a & b) / max(1, len(a))


def _score(R2, R3, pack):
    """以原文為主（2-gram）、舊譯為輔（3-gram）：盲翻材料常無現譯。"""
    og2, tr3 = pack or (set(), set())
    return max(ov(R2, og2), ov(R3, tr3))


def check_book(bk):
    d = os.path.join(T, '重譯', bk, '_材料')
    rep = os.path.join(T, '重譯', bk, '_盲翻_對齊', '回覆')
    if not os.path.isdir(rep):
        rep = os.path.join(T, '重譯', bk, '_盲翻', '回覆')
    if not (os.path.isdir(d) and os.path.isdir(rep)):
        return None
    mats = {}
    lens = {}
    for f in os.listdir(d):
        if f.endswith('.md'):
            md = MI.parse_md(io.open(os.path.join(d, f), encoding='utf-8').read())
            _mus = md.get('units', [])
            _og = ''.join(u.get('orig') or '' for u in _mus)
            _tr = ''.join(u.get('tr') or '' for u in _mus)
            mats[f[:-3]] = (grams(_og, 2), grams(_tr, 3))
            lens[f[:-3]] = len(_og)
    bad, ok, n = [], 0, 0
    for f in os.listdir(rep):
        if not f.endswith(SUF):
            continue
        k = f[:-len(SUF)]
        n += 1
        _txt = io.open(os.path.join(rep, f), encoding='utf-8').read()
        v = _score(grams(_txt, 2), grams(_txt, 3), mats.get(k))
        if v < MIN_SAME and lens.get(k, 999) > 15:
            bad.append((k, round(v, 3)))
        else:
            ok += 1
    miss = [k for k in mats if not os.path.exists(os.path.join(rep, k + SUF))]
    return dict(book=bk, mats=len(mats), reps=n, ok=ok, bad=bad, miss=len(miss))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--books', default='業疏,戒疏,尼鈔,行事鈔,義鈔,資持記')
    ap.add_argument('--strict', action='store_true')
    args = ap.parse_args()
    total_bad = 0
    for bk in [x.strip() for x in args.books.split(',') if x.strip()]:
        r = check_book(bk)
        if not r:
            print('%-4s 無法檢查（缺材料或回覆）' % bk)
            continue
        ratio = 100.0 * len(r['bad']) / max(1, r['reps'])
        total_bad += len(r['bad'])
        print('%-4s 材料 %4d｜回覆 %4d｜正常 %4d｜錯位 %3d（%.1f%%）｜缺 %3d'
              % (r['book'], r['mats'], r['reps'], r['ok'], len(r['bad']), ratio, r['miss']))
        if r['bad']:
            print('     錯位例：', [k for k, _ in r['bad'][:8]])
    if args.strict and total_bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
