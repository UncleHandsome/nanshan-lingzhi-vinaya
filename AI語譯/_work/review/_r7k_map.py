import re, os, io, sys

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
nums = list(range(207, 257))
rows = []
chunks = {}
for n in nums:
    p = os.path.join(base, "校閱_7K", f"校閱_{n}.txt")
    if not os.path.exists(p):
        rows.append((str(n), "MISSING", ""))
        continue
    t = io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
    tags = re.findall(r"^【(\d{4}-\d{4})】(\S+)#(\d+)$", t, re.M)
    if not tags:
        rows.append((str(n), "NOTAG", ""))
        continue
    chunks.setdefault(tags[0][1], []).append(n)
    rows.append((str(n), f"{tags[0][1]}#{tags[0][2]}-{tags[-1][1]}#{tags[-1][2]}", str(len(tags))))

for r in rows:
    print("\t".join(r))
print("--- chunk groups ---")
for c, ns in chunks.items():
    print(c, ns[0], ns[-1], len(ns))
