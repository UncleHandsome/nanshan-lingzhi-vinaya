# -*- coding: utf-8 -*-
"""全書回拼：一般段定稿＋長段定稿＋短卷題，按原卷順序合成完整 .txt 並對帳。

用法：
  python -X utf8 _src/assemble_book.py --book 業疏
  python -X utf8 _src/assemble_book.py --book 業疏 --out 測試/重譯/業疏/_全書.txt
  python -X utf8 _src/assemble_book.py --book 業疏 --check-only
"""
import argparse
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import materials_io as MI          # noqa: E402
import mk_review_materials as M    # noqa: E402

LONG_MIN = 500


def _groups(mdir, chunk):
    """回傳該卷的 [(s0, g1, key)]，來源為 _材料 的 .json 或 .md。"""
    out = []
    if not os.path.isdir(mdir):
        return out
    _seen = set()
    for f in sorted(os.listdir(mdir)):
        if not f.endswith(('.md', '.json')):
            continue
        key = f[:-5] if f.endswith('.json') else f[:-3]
        if key in _seen:
            continue
        _seen.add(key)
        md = MI.load(mdir, key) or {}
        if not isinstance(md, dict):
            continue
        _ch = md.get('chunk')
        _s0 = md.get('s0')
        _g1 = md.get('g1')
        if not _ch:
            _ex = md.get('ex') or ''
            _m = re.search(r'，第 (\d+)', _ex)
            _m2 = re.match(r'^(?:《[^》]+》)?([^，]+)，', _ex)
            _ch = _m2.group(1) if _m2 else ''
            _s0 = int(_m.group(1)) - 1 if _m else 0
            _g1 = _s0 + 1
        if _ch != chunk:
            continue
        out.append((int(_s0 or 0), int(_g1 or 0), key))
    out.sort()
    return out


def assemble(book, out_path=None, check_only=False):
    spec = M.BOOKS[book]
    sd = os.path.join(B, spec['src'].replace('/', os.sep))
    root = os.path.join(B, '測試', '重譯', book)
    mdir = os.path.join(root, '_材料')
    fin = os.path.join(root, '_定稿')
    lfin = os.path.join(root, '_長段', '_定稿')
    lmap = os.path.join(root, '_長段', '_對應.json')
    long_map = {}
    if os.path.exists(lmap):
        for it in json.load(io.open(lmap, encoding='utf-8')):
            long_map.setdefault(it['chunk'], {})[it['idx']] = it.get('total', 1)

    out, miss = [], []
    exp_chars = got_chars = 0
    n_seg = n_done = n_missing = 0
    for fn in sorted(os.listdir(sd)):
        if not fn.endswith('.txt'):
            continue
        chunk = fn[:-4]
        a = [x.strip() for x in
             io.open(os.path.join(sd, fn), encoding='utf-8', errors='ignore')
             .read().split('\n')[spec.get('skip', 0):] if x.strip()]
        groups = _groups(mdir, chunk)
        covered = {}
        for s0, g1, key in groups:
            for k in range(s0, g1):
                covered[k] = key
        long_idx = 0
        i = 0
        while i < len(a):
            exp_chars += len(a[i])
            if i in covered:
                key = covered[i]
                n_seg += 1
                p = os.path.join(fin, key + '.txt')
                if os.path.exists(p):
                    out.append(io.open(p, encoding='utf-8').read().strip())
                    got_chars += len(a[i])
                    n_done += 1
                else:
                    miss.append('%s\t%s\t缺一般段定稿' % (chunk, key))
                    n_missing += 1
                i += 1
                continue
            if len(a[i]) >= LONG_MIN:
                n_seg += 1
                p = os.path.join(lfin, '%s_L%04d.txt' % (chunk, i + 1))
                if os.path.exists(p):
                    out.append(io.open(p, encoding='utf-8').read().strip())
                    got_chars += len(a[i])
                    n_done += 1
                else:
                    miss.append('%s\t長段 idx=%d\t缺長段定稿' % (chunk, long_idx))
                    n_missing += 1
                long_idx += 1
                i += 1
                continue
            if len(a[i]) <= 5:
                out.append(a[i])
                got_chars += len(a[i])
                n_done += 1
                n_seg += 1
            else:
                miss.append('%s\t第 %d 段\t未分組且非長段' % (chunk, i))
                n_missing += 1
                n_seg += 1
            i += 1

    print('%s：預期 %d 段／%d 字；完成 %d 段／%d 字；缺 %d'
          % (book, n_seg, exp_chars, n_done, got_chars, n_missing))
    if miss:
        print('  缺段清單前 10 筆：')
        for x in miss[:10]:
            print('   ', x)
    if check_only:
        return n_missing
    out_path = out_path or os.path.join(root, '_全書.txt')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    io.open(out_path, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    if miss:
        io.open(out_path + '.missing.txt', 'w', encoding='utf-8').write('\n'.join(miss) + '\n')
    print('  已寫出：', os.path.relpath(out_path, B))
    return n_missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True)
    ap.add_argument('--out', default='')
    ap.add_argument('--check-only', action='store_true')
    args = ap.parse_args()
    op = os.path.join(B, args.out.replace('/', os.sep)) if args.out else None
    bad = assemble(args.book, op, args.check_only)
    if bad:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
