import io
p = r"AI語譯/_work/review/_re0_build.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('''io.open(os.path.join(OUT, "skips.json"), "w", encoding="utf-8").write(''','''io.open(os.path.join(OUT, "applied.json"), "w", encoding="utf-8").write(
    json.dumps([{"gid": g, "book": b, "chunk": c, "seg": s2, "op": o[0]} for (b, c, s2), lst in ops.items() for g, o in lst], ensure_ascii=False, indent=1))
io.open(os.path.join(OUT, "skips.json"), "w", encoding="utf-8").write(''')
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
