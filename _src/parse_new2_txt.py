# -*- coding: utf-8 -*-
"""解析 new2.txt（篇11-20）→ hb_align_new2.json"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '合編材料', 'new2.txt')
OUT = os.path.join(B, 'AI語譯', '_work', 'hb_align_new2.json')

NOISE = re.compile(r'^(說明|註|備註|小結|以上|（|\(|AI|注意|解讀)')


def main():
    t = io.open(SRC, encoding='utf-8').read()
    parts = re.split(r'【工作表\s*(\d+)[:：]\s*篇\s*(\d+)_([^】]*)】', t)
    got = {}
    for i in range(1, len(parts), 4):
        sheet = int(parts[i]); pian = int(parts[i + 1]); body = parts[i + 3] if i + 3 < len(parts) else ''
        rows = []
        for line in body.split('\n'):
            if not line.strip().startswith('|'):
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) < 3:
                continue
            c0 = cells[0].strip('* ').strip()
            rng = cells[2]
            if '鈔序' in c0 or c0.startswith(':') or not c0:
                continue
            if NOISE.match(c0):
                continue
            m = re.match(r'^(\d+)', c0)
            if not m:
                continue
            c = int(m.group(1))
            nums = [int(x) for x in re.findall(r'\d+', rng)]
            if not nums:
                continue
            a, b = nums[0], (nums[1] if len(nums) > 1 else nums[0])
            if b < a:
                a, b = b, a
            rows.append((a, b, c))
        if rows:
            got[pian] = rows

    align = {}
    for pian, rows in sorted(got.items()):
        rows.sort()
        mx = max(b for a, b, c in rows)
        arr = [None] * (mx + 1)
        for a, b, c in rows:
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
    print('篇', sorted(int(k) for k in align))
    for k in sorted(align, key=int):
        a = align[k]
        print('  篇%-3s 記%4d 段, 最大鈔 %3d' % (k, len(a), max(a) if a else 0))


if __name__ == '__main__':
    main()
