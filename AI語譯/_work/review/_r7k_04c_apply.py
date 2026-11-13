import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(base, "AI語譯/out/04_比丘尼鈔")
args = [a for a in sys.argv[1:] if a != "--dry"]
dry = "--dry" in sys.argv[1:]
edits = []
for a in args:
    edits.extend(json.load(io.open(a, encoding="utf-8")))
texts = {}
for c in ("06a_卷下之下", "06b_卷下之下"):
    texts[c] = io.open(os.path.join(OUT, c + ".txt"), encoding="utf-8").read()
for i, e in enumerate(edits):
    c = e["chunk"]
    t = texts[c]
    n = t.count(e["old"])
    if n != 1:
        print("FAIL idx=%d count=%d p=%s seg=%s old=%r" % (i, n, e["p"], e["seg"], e["old"][:60]))
        sys.exit(2)
    texts[c] = t.replace(e["old"], e["new"], 1)
seen = {}
for e in edits:
    seen.setdefault((e["chunk"], e["seg"]), {"kinds": set(), "p": e["p"]})
    seen[(e["chunk"], e["seg"])]["kinds"].add(e["kind"])
print("edits ok:", len(edits), "segments:", len(seen))
for (c, s), v in sorted(seen.items(), key=lambda x: (x[0][0], x[0][1])):
    print("  ", c, s, v["p"], ",".join(sorted(v["kinds"])))
if not dry:
    for c, t in texts.items():
        io.open(os.path.join(OUT, c + ".txt"), "w", encoding="utf-8", newline="").write(t)
    print("written")
