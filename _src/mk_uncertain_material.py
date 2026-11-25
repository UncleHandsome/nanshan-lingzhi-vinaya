# -*- coding: utf-8 -*-
"""產「不確定（uncertain）待判」材料，供人工或外部 AI 判定。

每筆包含：書別、key、原文、現譯、審閱者提出的疑點。
輸出 不確定_待判_20261125/不確定材料.md（另依書分檔）。
"""
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_3k_review as R

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RAW = os.path.join(B, '六書_3K_跑_20261124', '輸出')
OUT = os.path.join(B, '不確定_待判_20261125')
HEAD_RE = re.compile(r'^##\s+([^／\n]+)／(.+?)\s*$', re.M)

HEAD = '''下面是《南山律典》白話審閱時，模型標為「不確定」的段落。
每筆都附：原文、目前白話、審閱者提出的疑點。

請逐筆判定，輸出 JSONL（每行一筆）：
{"key":"key","verdict":"fix|keep","translation":"若 fix 請給修正後完整白話，keep 則空字串","note":"一句理由"}
- fix：現譯確有錯誤，需改
- keep：現譯可接受，不必改
每筆都要輸出一行，不要 code fence、不要前言。
'''


def load(book):
    return {str(json.loads(x)['key']): json.loads(x)
            for x in io.open(os.path.join(B, '定稿', book + '.jsonl'), encoding='utf-8') if x.strip()}


def txt(r):
    segs = r.get('segments') or []
    if segs:
        return '\n'.join((s.get('display_source') or s.get('source') or '') for s in segs)
    return r.get('display_source') or r.get('source') or ''


def main():
    os.makedirs(OUT, exist_ok=True)
    km = R.all_segment_keys()
    rows = []
    for p in sorted(glob.glob(os.path.join(RAW, '*_回.txt'))):
        stem = os.path.basename(p)[:-6]
        book = stem.rsplit('_', 1)[-1]
        exp = [m.group(2).strip() for m in
               HEAD_RE.finditer(io.open(os.path.join(B, '六書_3K_20261124', stem + '.md'), encoding='utf-8').read())]
        for ln in io.open(p, encoding='utf-8'):
            s = ln.strip()
            if not s.startswith('{'):
                continue
            try:
                o = json.loads(s)
            except Exception:
                continue
            if str(o.get('status', '')).lower() != 'uncertain':
                continue
            k = str(o.get('key') or '').strip()
            mk = R.match_key(k, exp) or k
            ent = km.get('%s|%s' % (book, mk))
            if not ent:
                continue
            src = ent[4].get('source') or ''
            cur = ent[4].get('translation') or ''
            rows.append({'book': book, 'stem': stem, 'key': mk, 'src': src, 'cur': cur,
                         'note': str(o.get('note') or '').strip()})
    print('uncertain 共', len(rows))

    def render(group, title):
        L = [HEAD, '# %s（%d 筆）' % (title, len(group)), '']
        for n, r in enumerate(group, 1):
            L += ['---', '', '## [%d] %s／%s' % (n, r['book'], r['key']), '',
                  '**原文**', '', r['src'], '', '**現譯**', '', r['cur'], '',
                  '**疑點**', '', r['note'], '']
        return '\n'.join(L)

    io.open(os.path.join(OUT, '不確定材料.md'), 'w', encoding='utf-8', newline='\n').write(
        render(rows, '不確定待判'))
    by = {}
    for r in rows:
        by.setdefault(r['book'], []).append(r)
    for b, g in by.items():
        io.open(os.path.join(OUT, '不確定材料_%s.md' % b), 'w', encoding='utf-8', newline='\n').write(
            render(g, '不確定待判—' + b))
        print('  %-12s %2d 筆' % (b, len(g)))
    print('→', os.path.join(OUT, '不確定材料.md'))


if __name__ == '__main__':
    main()
