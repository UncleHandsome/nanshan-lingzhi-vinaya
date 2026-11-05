
# -*- coding: utf-8 -*-
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_ju_dui2.py'
s = io.open(p, encoding='utf-8').read()
start = s.index('    li=0; buckets=')
end = s.index("    FONT='DFKai-SB'")
new = '''    buckets=[[] for _ in paras]; nomatch=0
    for pi in range(len(paras)):
        sa, sb = ju2src(ps[pi]), ju2src(max(ps[pi]+1, pe[pi]-1))
        if sb <= sa: sb = sa + 1
        k0 = max(0, bisect.bisect_left(le, sa) - 1)
        got = []
        k = k0
        while k < len(lines) and ls[k] < sb:
            ov = min(le[k], sb) - max(ls[k], sa)
            if ov > 0.5 * (le[k] - ls[k]): got.append(k)
            k += 1
        buckets[pi] = got
        if not got: nomatch += 1
'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('patched', 'bisect.bisect_left' in s)
