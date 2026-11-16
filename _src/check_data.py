# -*- coding: utf-8 -*-
"""資料面健檢：原文／舊譯段數對齊＋超長無標點引文掃描（不呼叫 API）。"""
import io
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import mk_review_materials as M  # noqa: E402

PUNCT = '。！？，、；：'


def load_src(spec, chunk):
    p = os.path.join(B, spec['src'].replace('/', os.sep), chunk + '.txt')
    if not os.path.exists(p):
        return None, p
    a = [x.strip() for x in
         io.open(p, encoding='utf-8', errors='ignore').read().split('\n')[spec.get('skip', 0):]
         if x.strip()]
    return a, p


def load_tr(spec, chunk):
    p = os.path.join(B, spec['tr'].replace('/', os.sep), chunk + '.txt')
    if not os.path.exists(p):
        return None, p
    o = [x.strip() for x in re.split(r'(?:\r?\n){2,}',
                                     io.open(p, encoding='utf-8', errors='ignore').read()) if x.strip()]
    return o, p


def main():
    rep = []
    rep.append('# 資料面健檢報告\n')
    rep.append('## 一、原文與舊譯段數對齊\n')
    rep.append('| 書 | 卷數 | 對齊 | 不合 | 缺舊譯 | 缺原文 |')
    rep.append('|:--|--:|--:|--:|--:|--:|')
    for bk, spec in M.BOOKS.items():
        d = os.path.join(B, spec['src'].replace('/', os.sep))
        chunks = sorted(f[:-4] for f in os.listdir(d) if f.endswith('.txt')) if os.path.isdir(d) else []
        ok = bad = notr = nosrc = 0
        bad_list = []
        for ch in chunks:
            a, _ = load_src(spec, ch)
            o, _ = load_tr(spec, ch)
            if a is None:
                nosrc += 1
                continue
            if o is None:
                notr += 1
                bad_list.append('%s：缺舊譯' % ch)
                continue
            if len(a) == len(o):
                ok += 1
            else:
                bad += 1
                bad_list.append('%s：原文 %d／舊譯 %d' % (ch, len(a), len(o)))
        rep.append('| %s | %d | %d | %d | %d | %d |' % (bk, len(chunks), ok, bad, notr, nosrc))
        if bad_list:
            rep.append('')
            rep.append('**%s 不合清單（前 15）**：%s' % (bk, '；'.join(bad_list[:15])))

    rep.append('\n## 二、超長無標點引文（>720 字且 400 字內無句讀）\n')
    rep.append('| 書 | 超長行(>500) | 危險行(>720 無標點) | 範例 |')
    rep.append('|:--|--:|--:|:--|')
    for bk, spec in M.BOOKS.items():
        d = os.path.join(B, spec['src'].replace('/', os.sep))
        if not os.path.isdir(d):
            continue
        nlong = ndanger = 0
        sample = ''
        for fn in sorted(os.listdir(d)):
            if not fn.endswith('.txt'):
                continue
            a, _ = load_src(spec, fn[:-4])
            if not a:
                continue
            for x in a:
                if len(x) > 500:
                    nlong += 1
                if len(x) > 720:
                    # 檢查每 400 字窗口是否完全無句讀
                    bad = any(not any(c in PUNCT for c in x[i:i + 400])
                              for i in range(0, len(x) - 400, 200))
                    if bad:
                        ndanger += 1
                        if not sample:
                            sample = '%s：%s…' % (fn[:-4], x[:40])
        rep.append('| %s | %d | %d | %s |' % (bk, nlong, ndanger, sample or '—'))

    out = os.path.join(B, '測試', '_資料健檢報告.md')
    io.open(out, 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    print('\n'.join(rep))


if __name__ == '__main__':
    main()
