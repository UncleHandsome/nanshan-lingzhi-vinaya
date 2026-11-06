# -*- coding: utf-8 -*-
import io, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(D, '_a008_data.json'), encoding='utf-8'))
J = d['ji']
print('n', len(J))
for i in range(295, 320):
    print(i, len(J[i]), J[i][:60].replace('\n', ' '))
import collections
c = collections.Counter(len(x) for x in J)
print('len hist top', c.most_common(10))
print('total', sum(c.values()), 'sumlen', sum(len(x) for x in J))
