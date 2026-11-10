import csv, io, sys
sys.stdout.reconfigure(encoding="utf-8")
p=r"AI語譯\_work\review\fix_re8_g2.tsv"
raw=io.open(p,encoding="utf-8",newline="").read()
print("len",len(raw), "lines", raw.count("\n"))
lines=raw.split("\n")
print("first 3 lines:")
for l in lines[:3]: print(repr(l[:200]))
print("...")
print("last line:", repr(lines[-2][:200]) if len(lines)>1 else "")
# count fields per line
import collections
c=collections.Counter(len(l.split("\t")) for l in lines if l.strip())
print(c)
