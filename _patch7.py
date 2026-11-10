import io
p = r"AI語譯/_work/review/_re0_export.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('''md.append("| 套用條數 | %d | %d | 186 |" % (sum(1 for e in ents if e["book"].startswith("01")), sum(1 for e in ents if e["book"].startswith("02"))))''','''applied = json.load(io.open(os.path.join(OUT, "applied.json"), encoding="utf-8"))
ap = collections.Counter(a["book"] for a in applied)
md.append("| 套用條數 | %d | %d | %d |" % (ap.get("01_行事鈔",0), ap.get("02_戒疏",0), len(applied)))''')
s = s.replace('for gid, book, chunk, seg, sug, reason in mis:', 'for gid, book, chunk, seg, sug, reason in sorted(mis, key=lambda x: x[0]):')
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
