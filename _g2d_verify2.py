import json, io, re
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
def segs(path):
    t = io.open(path, encoding="utf-8").read()
    parts = [p.strip("\n") for p in re.split(r"\n\s*\n", t)]
    return [p for p in parts if p.strip()]
s = segs(r"AI語譯/out/資持記/14c_下二.txt")
print("paras", len(s))
for i,x in enumerate(s):
    if "開許指派道場大眾服役勞作" in x:
        print("found in para", i+1, "len", len(x))
        print("TAIL:", x[-120:])
        print("HEAD:", x[:80])
# check rows 36-39 align
for r in rows:
    if r["chunk"]=="14c_下二":
        idx=int(r["seg"])-1
        print(r["gid"], "seg", r["seg"], "align", idx<len(s) and s[idx]==r["current"])
