# -*- coding: utf-8 -*-
"""彙整補譯結果 → AI語譯/miss.txt，並（可選）寫回 AI語譯/out。

用法：python _src/apply_miss.py [--write]
"""
import os, io, re, json, sys, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'AI語譯', '_work', 'miss_input.json')
ROUT = os.path.join(B, 'AI語譯', '_work', 'misstr')
MISS = os.path.join(B, 'AI語譯', 'miss.txt')


def main():
    write = '--write' in sys.argv
    data = json.load(io.open(SRC, encoding='utf-8'))
    got = {}
    for p in sorted(glob.glob(os.path.join(ROUT, 'out_*.json'))):
        try:
            arr = json.load(io.open(p, encoding='utf-8'))
        except Exception as e:
            print('!! 讀不到', p, e)
            continue
        for it in arr:
            got[(os.path.basename(p), int(it['seg']))] = it['text'].strip()

    # 依 book/key 對應：out_NN 與批次檔同序
    batches = []
    for n, p in enumerate(sorted(glob.glob(os.path.join(ROUT, '[0-9][0-9].json'))), 1):
        meta = json.load(io.open(p, encoding='utf-8'))
        batches.append((os.path.join(ROUT, 'out_%02d.json' % n), meta))

    lines = ['# 補譯結果', '',
             '待補：戒疏 20b（109 段）、資持記 12a/12b（50 段）、義鈔 01b/02b（8 段）', '']
    applied = 0
    for outp, meta in batches:
        book, key = meta['book'], meta['key']
        segs = [x['seg'] for x in meta['segs']]
        trans = {}
        try:
            arr = json.load(io.open(outp, encoding='utf-8'))
            for it in arr:
                trans[int(it['seg'])] = it['text'].strip()
        except Exception as e:
            print('!!', outp, e)
        missing = [s for s in segs if s not in trans]
        print('%-14s %-18s 應 %3d 得 %3d 缺 %s' % (book, key, len(segs), len(trans), missing[:6]))
        lines.append('## %s　%s' % (book, key))
        lines.append('')
        for x in meta['segs']:
            t = trans.get(x['seg'], '')
            lines.append('### 段 %d' % x['seg'])
            lines.append('')
            lines.append('原：' + x['src'])
            lines.append('')
            lines.append('譯：' + (t if t else '（缺）'))
            lines.append('')
        # 寫回
        if write and not missing:
            tp = os.path.join(B, 'AI語譯', 'out', book, key + '.txt')
            ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
            if len(ps) < max(segs):
                print('!! 段數不足，跳過', book, key)
                continue
            for s, t in trans.items():
                ps[s - 1] = t
            io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(ps) + '\n')
            applied += len(trans)
    io.open(MISS, 'w', encoding='utf-8').write('\n'.join(lines))
    print('miss.txt 已寫出；寫回段數', applied)


if __name__ == '__main__':
    main()
