import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(base, "AI語譯/out/04_比丘尼鈔")
# collect modified (chunk, seg) from all edit files
mods = {}
for fn in os.listdir(os.path.join(base, "AI語譯/_work/review")):
    if fn.startswith("_r7k_04c_e") and fn.endswith(".json"):
        for e in json.load(io.open(os.path.join(base, "AI語譯/_work/review", fn), encoding="utf-8")):
            mods.setdefault(e["chunk"], set()).add(e["seg"])
which = sys.argv[1]
chunk = "06a_卷下之下" if which == "a" else "06b_卷下之下"
lines = [x for x in io.open(os.path.join(OUT, chunk + ".txt"), encoding="utf-8").read().split("\n")]
# out segment n is at nonempty index n-1
nonempty = [x for x in lines if x.strip()]
for seg in sorted(mods[chunk]):
    print("【%s#%d】%s" % (chunk[:3], seg, nonempty[seg - 1]))
    print()
