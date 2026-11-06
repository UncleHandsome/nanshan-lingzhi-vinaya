# -*- coding: utf-8 -*-
"""解析 new.txt 的人工對應表 → new_align.json（篇 → 記段→鈔序，0=篇前）"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '合編材料', 'new.txt')
OUT = os.path.join(B, 'AI語譯', '_work', 'hb_align_new.json')


def main():
    t = io.open(SRC, encoding='utf-8').read()
    # 切成工作表段落
    parts = re.split(r'【工作表\s*(\d+)】\s*([^\n]*)', t)
    sheets = {}
    for i in range(1, len(parts), 3):
        no = int(parts[i])
        title = parts[i + 1]
        body = parts[i + 2] if i + 2 < len(parts) else ''
        m = re.search(r'篇\s*(\d+)', title)
        if not m:
            continue
        pian = int(m.group(1))
        rows = []
        for line in body.split('\n'):
            if not line.strip().startswith('|'):
                continue
            cells = [c.strip().strip('*').strip() for c in line.strip().strip('|').split('|')]
            if len(cells) < 3:
                continue
            c0 = cells[0].strip('* ').strip()
            rng = cells[2]
            if c0 in ('鈔序', ':---:', '') or '鈔文提要' in c0:
                continue
            rows.append((c0, rng))
        if rows:
            sheets.setdefault(pian, []).extend(rows)
    print('篇數', len(sheets), '列', sum(len(v) for v in sheets.values()))

    align = {}
    LIMIT = 10
    for pian, rows in sorted(sheets.items()):
        if pian > LIMIT:
            continue
        pairs = []
        for c0, rng in rows:
            if c0 in ('篇前', '前言', '卷前'):
                c = 0
            else:
                m = re.match(r'(\d+)', c0)
                if not m:
                    continue
                c = int(m.group(1))
            nums = [int(x) for x in re.findall(r'\d+', rng)]
            if not nums:
                continue
            a = nums[0]
            b = nums[1] if len(nums) > 1 else a
            if b < a:
                a, b = b, a
            pairs.append((a, b, c))
        if not pairs:
            continue
        pairs.sort()
        mx = max(b for a, b, c in pairs)
        arr = [None] * (mx + 1)
        for a, b, c in pairs:
            for z in range(a, min(b, mx) + 1):
                arr[z] = c
        last = 0
        for i in range(1, mx + 1):
            if arr[i] is None:
                arr[i] = last
            else:
                last = arr[i]
        align[str(pian)] = arr[1:]
    json.dump(align, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('對齊篇', len(align), '記段', sum(len(v) for v in align.values()))
    for k in sorted(align, key=int):
        print('  篇%-3s %d 段, max鈔 %d, 篇前 %d' % (k, len(align[k]), max(align[k] or [0]),
                                                sum(1 for x in align[k] if x == 0)))


if __name__ == '__main__':
    main()
