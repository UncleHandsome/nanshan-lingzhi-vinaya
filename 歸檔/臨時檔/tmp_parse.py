# -*- coding: utf-8 -*-
import re, json, html as htmlmod

p = r"docs/hebian/卷中之二.html"
s = open(p, encoding="utf-8").read()

# find all pair blocks
pairs = []
for m in re.finditer(r'<div class="pair" id="(s\d+)">(.*?)</div></div>', s, re.S):
    pass

# safer: split on pair divs
starts = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="pair" id="(s\d+)">', s)]
print("count", len(starts))
blocks = []
for i, (pos, sid) in enumerate(starts):
    end = starts[i+1][0] if i+1 < len(starts) else len(s)
    blocks.append((sid, s[pos:end]))

def strip_tags(x):
    x = re.sub(r'<br\s*/?>', '\n', x)
    x = re.sub(r'<[^>]+>', '', x)
    return htmlmod.unescape(x)

rows = []
for sid, b in blocks:
    # o / o2 div, t div
    mo = re.search(r'<div class="(o2?)">(.*?)</div><div class="t">(.*?)</div>', b, re.S)
    if not mo:
        print("NOMATCH", sid, b[:200])
        continue
    cls = mo.group(1)
    orig = strip_tags(mo.group(2)).strip()
    trans = strip_tags(mo.group(3)).strip()
    typ = orig[:3]
    body = orig[3:] if typ.startswith("【") else orig
    rows.append({"id": sid, "cls": cls, "orig": orig, "trans": trans})

json.dump(rows, open("tmp_rows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rows", len(rows))
for r in rows[:6]:
    print(r["id"], r["cls"], r["orig"][:20], "||", r["orig"][-20:])
