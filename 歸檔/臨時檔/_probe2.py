import re, io
p = r"校閱批次/new/已完成/re0/re0.txt"
lines = io.open(p, encoding="utf-8-sig").read().split("\n")
for i, ln in enumerate(lines):
    if re.search(r"\d{3}-\d{4}.*#\d+.*P[012]", ln) and not ln.startswith("### "):
        print(i+1, repr(ln[:100]))
