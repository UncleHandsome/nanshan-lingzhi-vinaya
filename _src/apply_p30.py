# -*- coding: utf-8 -*-
"""套用使用者提供的篇30（諸部別行）對應表"""
import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
# (鈔序, 記起, 記迄)
ROWS = [
    (2, 1, 6), (3, 6, 8), (4, 8, 9), (5, 10, 11), (6, 11, 11),
    (7, 11, 14), (8, 15, 16), (9, 16, 16), (10, 16, 16), (11, 16, 17),
    (12, 17, 18), (13, 18, 18), (14, 18, 19), (15, 19, 19), (16, 19, 19),
    (17, 19, 19), (18, 19, 20), (19, 20, 21), (20, 21, 22), (21, 22, 22),
    (22, 22, 23), (23, 23, 25), (24, 25, 26), (24, 26, 28),
]
N = 53


def main():
    arr = [None] * (N + 1)
    for c, a, b in ROWS:
        for z in range(a, min(b, N) + 1):
            arr[z] = c
    # 記 29 以後：表中未列，接在最後一條鈔（24）之後
    for z in range(29, N + 1):
        if arr[z] is None:
            arr[z] = 24
    last = 0
    for i in range(1, N + 1):
        arr[i] = last if arr[i] is None else arr[i]
        last = arr[i]
    p = os.path.join(B, 'AI語譯', '_work', 'hb_align.json')
    m = json.load(io.open(p, encoding='utf-8'))
    m['29'] = arr[1:]
    json.dump(m, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    print('篇30 對應已寫入，長度', len(arr) - 1)
    print('前 12 段對應鈔號:', arr[1:13])


if __name__ == '__main__':
    main()
