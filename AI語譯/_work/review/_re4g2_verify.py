# -*- coding: utf-8 -*-
import json
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
outs = json.load(open(r'AI語譯/_work/review/_re4g2_out_rows.json', encoding='utf-8'))
curmap = {}
for d in rows:
    curmap[(d['book'], d['chunk'], d['seg'])] = d['current']

f = open(r'AI語譯/_work/review/_re4g2_verify.txt', 'w', encoding='utf-8')
for k, (book, chunk, seg, new) in enumerate(outs):
    cur = curmap[(book, chunk, seg)]
    n = min(len(cur), len(new))
    i = 0
    while i < n and cur[i] == new[i]:
        i += 1
    j, ki = len(cur) - 1, len(new) - 1
    while j >= i and ki >= i and cur[j] == new[ki]:
        j -= 1; ki -= 1
    old_mid, new_mid = cur[i:j+1], new[i:ki+1]
    f.write("### %d %s seg=%s  clen=%d->%d\n" % (k, chunk, seg, len(cur), len(new)))
    f.write("  pre : %s\n" % cur[max(0, i-22):i])
    f.write("  OLD : %s\n" % old_mid)
    f.write("  NEW : %s\n" % new_mid)
    f.write("  post: %s\n\n" % cur[j+1:j+1+22])
f.close()
print("ok", len(outs))
