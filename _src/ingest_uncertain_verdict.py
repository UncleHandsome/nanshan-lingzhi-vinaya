# -*- coding: utf-8 -*-
"""把「不確定待判」的回覆（verdict fix/keep）寫回回覆檔。

輸入 JSONL：{"key":"書／mk","verdict":"fix|keep","translation":"...","note":"..."}
- fix  → 該行改成 status=fixed、translation=新譯（之後 rebuild_fixes 會收進 fixes）
- keep → 該行改成 status=ok（不再出現在不確定清單）
找不到對應行時會列出，不會靜默丟掉。
"""
import glob
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RAW = os.path.join(B, '六書_3K_跑_20261124', '輸出')
HEAD_RE = re.compile(r'^##\s+([^／\n]+)／(.+?)\s*$', re.M)


def main():
    src = sys.argv[1]
    dry = '--dry' in sys.argv
    # 檔名 -> 標題 key 集合
    keys_of = {}
    for p in glob.glob(os.path.join(B, '六書_3K_20261124', '*.md')):
        stem = os.path.basename(p)[:-3]
        keys_of[stem] = {m.group(2).strip() for m in HEAD_RE.finditer(io.open(p, encoding='utf-8').read())}
    # 目標：book|mk -> stem（完整 key 精確比對）
    target = {}
    for stem, ks in keys_of.items():
        book = stem.rsplit('_', 1)[-1]
        for k in ks:
            target.setdefault((book, k), stem)

    want = {}
    for ln in io.open(src, encoding='utf-8'):
        s = ln.strip()
        if not s.startswith('{'):
            continue
        o = json.loads(s)
        raw = str(o.get('key') or '')
        book, _, mk = raw.partition('／')
        book = book.strip()
        mk = mk.strip()
        if (book, mk) not in target:
            # 試剝尾碼
            kk = mk
            while '-' in kk and (book, kk) not in target:
                kk = kk.rsplit('-', 1)[0]
            if (book, kk) in target:
                mk = kk
        want[(book, mk)] = o
    print('讀到 %d 筆判定' % len(want))

    by_stem = {}
    for (book, mk), o in want.items():
        stem = target.get((book, mk))
        if not stem:
            print('  找不到對應：%s／%s' % (book, mk))
            continue
        by_stem.setdefault(stem, {})[mk] = o

    done = 0
    for stem, patch in sorted(by_stem.items()):
        p = os.path.join(RAW, stem + '_回.txt')
        if not os.path.exists(p):
            print('  缺回覆檔：%s' % stem)
            continue
        lines = io.open(p, encoding='utf-8').read().split('\n')
        out = []
        hit = 0
        for ln in lines:
            s = ln.strip()
            if not s.startswith('{'):
                out.append(ln)
                continue
            try:
                o = json.loads(s)
            except Exception:
                out.append(ln)
                continue
            k = str(o.get('key') or '').strip()
            if k in patch:
                v = patch[k]
                verdict = str(v.get('verdict') or '').strip().lower()
                if verdict == 'fix' and (v.get('translation') or '').strip():
                    o['status'] = 'fixed'
                    o['translation'] = v['translation']
                else:
                    o['status'] = 'ok'
                    o['translation'] = ''
                o['note'] = str(v.get('note') or o.get('note') or '')[:300]
                o['verdict'] = 'fix' if verdict == 'fix' else 'keep'
                out.append(json.dumps(o, ensure_ascii=False))
                hit += 1
            else:
                out.append(ln)
        if hit:
            done += hit
            if not dry:
                io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
            print('  %-24s 套用 %d 筆' % (stem, hit))
        else:
            print('  %-24s 找不到相符行' % stem)
    print('共套用 %d 筆%s' % (done, '（dry-run）' if dry else ''))


if __name__ == '__main__':
    main()
