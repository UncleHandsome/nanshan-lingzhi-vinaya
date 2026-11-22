# -*- coding: utf-8 -*-
"""把盲翻回覆對齊到現行材料：以 3-gram 重合率配對，產出 _盲翻_對齊/回覆。

用法： python -X utf8 _src/realign_blind.py --books 業疏,行事鈔,義鈔
"""
import argparse
import io
import os
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, '測試')
sys.path.insert(0, os.path.join(B, '_src'))
import materials_io as MI  # noqa: E402

SUF = '_回.txt'
MIN_SAME = 0.06      # 與同 key 材料低於此值 → 視為錯位
MIN_MATCH = 0.18     # 重新配對的最低門檻


def grams(t, n=3):
    s = ''.join(ch for ch in t if '\u4e00' <= ch <= '\u9fff')
    return set(s[i:i + n] for i in range(0, max(0, len(s) - n + 1)))


def ov(a, b):
    return len(a & b) / max(1, len(a))


def _score(R2, R3, pack):
    """原文為主（2-gram）、舊譯為輔（3-gram）；舊譯缺失時仍可判位。"""
    og2, tr3 = pack or (set(), set())
    return max(ov(R2, og2), ov(R3, tr3))


def do_book(bk):
    d = os.path.join(T, '重譯', bk, '_材料')
    rep = os.path.join(T, '重譯', bk, '_盲翻', '回覆')
    dst = os.path.join(T, '重譯', bk, '_盲翻_對齊', '回覆')
    os.makedirs(dst, exist_ok=True)

    mats = {}
    _lens = {}
    for f in os.listdir(d):
        if f.endswith('.md'):
            md = MI.parse_md(io.open(os.path.join(d, f), encoding='utf-8').read())
            _og = ''.join(u.get('orig') or '' for u in md.get('units', []))
            _tr = ''.join(u.get('tr') or '' for u in md.get('units', []))
            mats[f[:-3]] = (grams(_og, 2), grams(_tr, 3))
            _lens[f[:-3]] = len(_og)

    reps = {}
    for f in os.listdir(rep):
        if f.endswith(SUF):
            _t = io.open(os.path.join(rep, f), encoding='utf-8').read()
            reps[f[:-len(SUF)]] = (grams(_t, 2), grams(_t, 3))

    same = {k: _score(v[0], v[1], mats.get(k)) for k, v in reps.items()}
    # 極短段（<=15 字）不因重合率偏低就判錯位，避免誤丟正確短標目
    bad = [k for k, v in same.items() if v < MIN_SAME and _lens.get(k, 999) > 15]
    badset = set(bad)

    assign = {}
    orphans = []
    for k in bad:
        R2, R3 = reps[k]
        best_v, best_k = 0.0, None
        for mk, mg in mats.items():
            if mk in badset or mk not in reps:          # 只挑「目前沒有可用回覆」的目標
                v = _score(R2, R3, mg)
                if v > best_v:
                    best_v, best_k = v, mk
        if best_k and best_v >= MIN_MATCH:
            assign.setdefault(best_k, []).append((best_v, k))
        else:
            orphans.append(k)

    final = {}
    for k, (R2, R3) in reps.items():
        if k not in badset:
            final[k] = (k, _score(R2, R3, mats.get(k)))
    for mk, cands in assign.items():
        cands.sort(reverse=True)
        final[mk] = (cands[0][1], cands[0][0])
        for _v, _k in cands[1:]:
            orphans.append(_k)          # 多對一的落選者不再靜默消失

    for mk, (src_k, score) in final.items():
        shutil.copy2(os.path.join(rep, src_k + SUF), os.path.join(dst, mk + SUF))
        _us = os.path.join(rep, src_k + '_usage.json')
        if os.path.exists(_us):
            shutil.copy2(_us, os.path.join(dst, mk + '_usage.json'))

    miss = [k for k in mats if k not in final]
    print('%s：材料 %d｜回覆 %d｜對齊 %d｜孤兒 %d｜仍缺 %d'
          % (bk, len(mats), len(reps), len(final), len(orphans), len(miss)), flush=True)
    if orphans:
        io.open(os.path.join(T, '重譯', bk, '_盲翻_對齊', '_孤兒.txt'), 'w',
                encoding='utf-8').write('\n'.join(orphans))
    if miss:
        io.open(os.path.join(T, '重譯', bk, '_盲翻_對齊', '_缺漏.txt'), 'w',
                encoding='utf-8').write('\n'.join(miss))
    return len(final), len(orphans), len(miss)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--books', default='業疏,戒疏,尼鈔,行事鈔,義鈔,資持記')
    args = ap.parse_args()
    for bk in [x.strip() for x in args.books.split(',') if x.strip()]:
        do_book(bk)


if __name__ == '__main__':
    main()
