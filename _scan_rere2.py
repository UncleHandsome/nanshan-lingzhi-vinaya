import re, sys, os

s = open(r'待跑_審查擋掉\rere.txt', encoding='utf-8-sig').read()
lines = s.splitlines()

# map first line index (1-based) where each file number appears
firsts = {}
for n, l in enumerate(lines, 1):
    for m in re.finditer(r'【(\d{3})-(\d{4})】', l):
        f = m.group(1)
        if f not in firsts:
            firsts[f] = n
for f, n in sorted(firsts.items(), key=lambda kv: kv[1]):
    print(f, n, repr(lines[n-1][:80]))
