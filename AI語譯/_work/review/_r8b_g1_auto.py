# -*- coding: utf-8 -*-
import json, io, os, re

base = os.path.dirname(os.path.abspath(__file__))
rows = json.load(io.open(os.path.join(base, "_r8b_g1_rows.json"), encoding="utf-8"))

out = io.open(os.path.join(base, "_r8b_g1_auto.txt"), "w", encoding="utf-8")
stats = {"pair": 0, "applied": 0, "manual": 0}

pat_pair = re.compile(r'「([^」]{2,60})」\s*(?:改為|改作|改回|改写作|改译)\s*「([^」]{1,80})」')
pat_pair2 = re.compile(r'改\s*「([^」]{2,60})」\s*(?:為|作)\s*「([^」]{1,80})」')
pat_del = re.compile(r'刪(?:去|除)\s*「([^」]{1,40})」[，,]?\s*(?:改為|改作)\s*「([^」]{2,80})」')
pat_only = re.compile(r'(?:改為|改作|作)\s*「([^」]{2,80})」')

for i, r in enumerate(rows):
    c = r["current"]
    s = r["suggestion"]
    ops = []
    m = pat_pair.search(s)
    if not m:
        m = pat_pair2.search(s)
    status = ""
    if m:
        old, new = m.group(1), m.group(2)
        n_old = c.count(old)
        if n_old == 1 and new not in c:
            ops.append((old, new))
            status = "PAIR_OK"
        elif n_old == 0 and new in c:
            status = "APPLIED"
        else:
            status = "PAIR_AMBIG n_old=%d new_in=%s" % (n_old, new in c)
    else:
        m2 = pat_del.search(s)
        if m2:
            status = "DELPAT old=%s" % m2.group(1)
        else:
            m3 = pat_only.search(s)
            status = "ONLYNEW new=%s" % (m3.group(1) if m3 else "")
    out.write("%d\t%s\t%s\n" % (i, status, s[:60]))
    if status == "PAIR_OK":
        stats["pair"] += 1
    elif status == "APPLIED":
        stats["applied"] += 1
    else:
        stats["manual"] += 1
out.close()
print(stats)
