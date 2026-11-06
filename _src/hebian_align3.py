import io, os, re, json
import numpy as np
import importlib.util

spec = importlib.util.spec_from_file_location('a2', r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\hebian_align2.py')
a2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a2)


def main():
    secs = a2.sections()
    zs = a2.zsections()
    out = {}
    tot = hit = 0
    for idx, sec in enumerate(secs):
        zi = zs[idx]['items'] if idx < len(zs) else []
        C = [a2.grams(o) for o, t in sec['items']]
        Z = [a2.grams(o) for o, t in zi]
        m = max(1, len(C))
        assigned = []
        for i in range(len(zi)):
            best, bj = 0, None
            for j, c in enumerate(C):
                if not Z[i] or not c:
                    continue
                inter = len(Z[i] & c)
                if inter > best:
                    best, bj = inter, j
            assigned.append(bj)
        # 單調化：只允許前進，遇到倒退則沿用前值
        last = 0
        for k in range(len(assigned)):
            if assigned[k] is None:
                continue
            assigned[k] = max(last, assigned[k])
            last = assigned[k]
        # 內插空缺
        ks = [k for k, v in enumerate(assigned) if v is not None]
        if ks:
            for k in range(len(assigned)):
                if assigned[k] is not None:
                    continue
                prev = max([x for x in ks if x < k], default=None)
                nxt = min([x for x in ks if x > k], default=None)
                if prev is None:
                    assigned[k] = assigned[nxt]
                elif nxt is None:
                    assigned[k] = assigned[prev]
                else:
                    frac = (k - prev) / (nxt - prev)
                    assigned[k] = int(round(assigned[prev] + frac * (assigned[nxt] - assigned[prev])))
        assigned = [0 if v is None else int(v) for v in assigned]
        out[str(idx)] = assigned
        for k, (o, t) in enumerate(zi):
            tot += 1
            if Z[k] & C[assigned[k]]:
                hit += 1
    print('記段', tot, '對到有 4-gram 交集 %.1f%%' % (100.0 * hit / max(1, tot)))
    json.dump(out, io.open(os.path.join(a2.B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('saved')


if __name__ == '__main__':
    main()
