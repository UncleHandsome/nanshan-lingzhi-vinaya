import re, io, os, json, difflib, sys
sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
rows = json.load(io.open(os.path.join(base, "AI語譯/_work/review/_r7k_04c_segs.json"), encoding="utf-8"))
outs = {}
for c in ("06a_卷下之下", "06b_卷下之下"):
    outs[c] = [x for x in io.open(os.path.join(base, "AI語譯/out/04_比丘尼鈔", c + ".txt"), encoding="utf-8").read().split("\n") if x.strip()]
for r in rows:
    if r["ok"]:
        continue
    print("=== packet", r["packet"], "seg", r["chunk"], r["seg"])
    cand = outs[r["chunk"]][r["seg"] - 1]
    print("PACKET:", r["tr"][:120])
    print("OUT   :", cand[:120])
    sm = difflib.SequenceMatcher(None, r["tr"], cand)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print("  ", tag, repr(r["tr"][i1:i2])[:80], "->", repr(cand[j1:j2])[:80])
