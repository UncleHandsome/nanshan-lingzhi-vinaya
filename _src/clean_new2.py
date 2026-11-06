# -*- coding: utf-8 -*-
"""清理 new2.txt：只留表格資料，記下 Sheet/記序 參照，輸出 CSV 與統計"""
import io, os, re, csv

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '合編材料', 'new2.txt')
OUT = os.path.join(B, '合編材料', 'new2_clean.csv')
REP = os.path.join(B, '合編材料', 'new2_clean_report.txt')

HEAD = re.compile(r'^#{2,4}\s*[一二三四五六七八九十]+、\s*【工作表\s*(\d+)[:：]\s*篇\s*(\d+)_([^】]*)】')
ALT = re.compile(r'^#{2,4}\s*【工作表\s*(\d+)】\s*篇\s*(\d+)_([^：:]*)[：:]')


def main():
    lines = io.open(SRC, encoding='utf-8').read().split('\n')
    cur = None
    rows = []
    for ln in lines:
        m = HEAD.match(ln) or ALT.match(ln)
        if m:
            cur = (int(m.group(1)), int(m.group(2)), m.group(3).strip())
            continue
        if not ln.strip().startswith('|'):
            continue
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        if len(cells) < 3 or not cur:
            continue
        c0 = cells[0].replace('*', '').strip()
        if not re.match(r'^(?:\d+|篇前|開卷|篇題)', c0):
            continue
        if '鈔序' in c0:
            continue
        rng = cells[2]
        note = cells[3] if len(cells) > 3 else ''
        # 抽出所有 Sheet/記參照
        refs = re.findall(r'(?:Sheet\s*(\d+)\s*記\s*)?(\d+)(?:\s*[~～-]\s*(\d+))?\s*(?:\(([^)]*)\))?', rng)
        sheets = sorted(set(int(r[0]) for r in refs if r[0]))
        nums = [int(r[1]) for r in refs]
        clean = re.sub(r'\s+', ' ', rng).strip()
        rows.append(dict(sheet_m=cur[0], pian_m=cur[1], pian=cur[2], chao=c0,
                         refs=clean, sheets=','.join(str(s) for s in sheets),
                         nmin=(min(nums) if nums else ''), nmax=(max(nums) if nums else ''),
                         note=re.sub(r'\s+', ' ', note)[:120]))
    with io.open(OUT, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['pian', 'chao', 'refs', 'sheets', 'nmin', 'nmax', 'note', 'sheet_m', 'pian_m'])
        w.writeheader()
        w.writerows(rows)
    by_pian = {}
    for r in rows:
        by_pian.setdefault(r['pian'], []).append(r)
    out = ['new2.txt 清理報告', '=' * 20, '總列數 %d' % len(rows), '']
    for p, rs in sorted(by_pian.items()):
        sh = sorted(set(x['sheets'] for x in rs))
        out.append('篇%-4s 列%-3d 參照工作表 %s  記號 %s~%s' % (
            p, len(rs), '|'.join(sh), min(x['nmin'] for x in rs if x['nmin'] != ''),
            max(x['nmax'] for x in rs if x['nmax'] != '')))
    io.open(REP, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
