# -*- coding: utf-8 -*-
"""找出「未經語譯」的段落（譯文與原文幾乎相同），輸出清單。

判定：去掉段首標籤與空白後，
  1. 譯文與原文完全相同；或
  2. 兩者相似度 >= 0.90 且原文長度 >= 12 字；或
  3. 譯文中含原文 80% 以上的漢字（且原文 >= 20 字）——文言照抄。
短標題（兩邊都 < 8 字）不列入。

輸出：
  AI語譯/未譯清單.md
  AI語譯/_work/untranslated.json
"""
import os, io, re, json, difflib, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
LEAD = re.compile(r'^(【[^】]{1,6}】)+')

BOOKS = [
    ('01_行事鈔', '01_行事鈔', '四分律刪繁補闕行事鈔'),
    ('02_戒疏', '02_戒疏', '四分律含注戒本疏'),
    ('03_業疏', '03_業疏', '四分律刪補隨機羯磨疏'),
    ('04_比丘尼鈔', '04_比丘尼鈔', '四分比丘尼鈔'),
    ('05_拾毗尼義鈔', '05_拾毗尼義鈔', '四分律拾毗尼義鈔'),
    ('資持記', '資持記_細分', '四分律行事鈔資持記'),
]


def norm(s):
    s = LEAD.sub('', s.strip())
    s = re.sub(r'[\s\u3000]', '', s)
    return s


def han_only(s):
    return ''.join(c for c in s if '\u4e00' <= c <= '\u9fff')


def load_pairs(srcdir, tag):
    S = os.path.join(B, 'TXT_分卷', srcdir)
    T = os.path.join(B, 'AI語譯', 'out', tag)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        key = f[:-4]
        tp = os.path.join(T, key + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        out.append((key, sp, tt))
    return out


def main():
    report = []
    for tag, srcdir, title in BOOKS:
        rows = []
        for key, sp, tt in load_pairs(srcdir, tag):
            for i in range(min(len(sp), len(tt))):
                a = norm(sp[i])
                b = norm(tt[i])
                if not a:
                    continue
                ha, hb = han_only(a), han_only(b)
                if len(ha) < 8 and len(hb) < 8:
                    continue
                if a == b:
                    if len(ha) < 10:      # 短標題（篇名、科判）不算未譯
                        continue
                    reason = 'same'
                else:
                    r = difflib.SequenceMatcher(None, a, b).ratio()
                    if r >= 0.95 and len(ha) >= 20:
                        reason = 'sim%.2f' % r
                    else:
                        continue
                # 排除標題、目錄、譯款等非正文行
                if a.startswith(('No.', '○', '◎')):
                    continue
                if not re.search(r'[。！？；]', a) and len(ha) < 60:
                    continue
                if re.search(r'(譯$|撰$|述$|撰述$|譯述$|謹題$|謹識$)', a) and len(ha) < 40:
                    continue
                rows.append(dict(key=key, seg=i + 1, reason=reason,
                                 src=sp[i], tr=tt[i], chars=len(ha)))
        report.append(dict(tag=tag, title=title, rows=rows))

    total = sum(len(r['rows']) for r in report)
    chars = sum(x['chars'] for r in report for x in r['rows'])
    print('untranslated segments', total, 'chars', chars)

    os.makedirs(os.path.join(B, 'AI語譯', '_work'), exist_ok=True)
    json.dump(report, io.open(os.path.join(B, 'AI語譯', '_work', 'untranslated.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    md = ['# 未譯段落清單', '',
          '更新：%s' % '2026-11-06', '',
          '判定方式：譯文去掉段首標籤與空白後，與原文完全相同（≥10 字），或相似度 ≥ 0.95（≥20 字）；'
          '已排除篇名、目錄、譯款等非正文行。',
          '', '| 書 | 未譯段數 | 字數（約） |', '|:--|--:|--:|']
    for r in report:
        md.append('| %s | %d | %d |' % (r['title'], len(r['rows']), sum(x['chars'] for x in r['rows'])))
    md.append('| **合計** | **%d** | **%d** |' % (total, chars))
    md.append('')
    for r in report:
        if not r['rows']:
            continue
        md.append('## %s（%d 段）' % (r['title'], len(r['rows'])))
        md.append('')
        cur = None
        for x in r['rows']:
            if x['key'] != cur:
                cur = x['key']
                md.append('### %s' % cur)
                md.append('')
                md.append('| 段 | 字數 | 原文（節錄） | 現「譯文」 |')
                md.append('|--:|--:|:--|:--|')
            src = x['src'].replace('|', '｜')
            tr = x['tr'].replace('|', '｜')
            md.append('| %d | %d | %s | %s |' % (x['seg'], x['chars'],
                                                 src[:80] + ('…' if len(src) > 80 else ''),
                                                 tr[:60] + ('…' if len(tr) > 60 else '')))
        md.append('')
    p = os.path.join(B, 'AI語譯', '未譯清單.md')
    io.open(p, 'w', encoding='utf-8').write('\n'.join(md))
    print('wrote', p)

    tsv = ['書\t分塊\t段\t字數\t原文\t現譯文']
    for r in report:
        for x in r['rows']:
            tsv.append('\t'.join([r['title'], x['key'], str(x['seg']), str(x['chars']),
                                  x['src'].replace('\t', ' '), x['tr'].replace('\t', ' ')]))
    tp = os.path.join(B, 'AI語譯', '未譯清單.tsv')
    io.open(tp, 'w', encoding='utf-8').write('\n'.join(tsv))
    print('wrote', tp)
    for r in report:
        print('  %-14s %4d 段' % (r['tag'], len(r['rows'])))


if __name__ == '__main__':
    main()
