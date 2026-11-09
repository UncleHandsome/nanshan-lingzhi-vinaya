# -*- coding: utf-8 -*-
import io, json
raw = io.open(r'AI語譯/_work/review/fix_re4_g2.tsv', encoding='utf-8').read().split('\n')[:-1]
rows = [l.split('\t') for l in raw]
want = {('03_業疏', '17b_卷三之六', '7'), ('03_業疏', '17b_卷三之六', '102'),
        ('資持記', '16e_下四', '4'), ('資持記', '10b_中三下', '63'),
        ('資持記', '15d_下三', '13'), ('01_行事鈔', '11b_卷下之三', '22'),
        ('資持記', '11c_中四上', '23'), ('資持記', '17a_卷三之六', '70')}
f = open(r'AI語譯/_work/review/_re4g2_spot.txt', 'w', encoding='utf-8')
for r in rows:
    k = (r[0], r[1], r[2])
    if k in want:
        f.write("=== %s %s seg=%s\n%s\n\n" % (r[0], r[1], r[2], r[3]))
f.close()
