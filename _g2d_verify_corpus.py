import json, io, re
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
def segs(path):
    t = io.open(path, encoding="utf-8").read()
    parts = [p.strip("\n") for p in re.split(r"\n\s*\n", t)]
    return [p for p in parts if p.strip()]
for book, chunk, path in [("05_拾毗尼義鈔","03b_卷中之一", r"AI語譯/out/05_拾毗尼義鈔/03b_卷中之一.txt"),
                          ("05_拾毗尼義鈔","04a_卷中之二", r"AI語譯/out/05_拾毗尼義鈔/04a_卷中之二.txt")]:
    s = segs(path)
    print(book, chunk, "paras", len(s))
    for r in rows:
        if r["chunk"]==chunk:
            idx=int(r["seg"])-1
            hit = idx<len(s) and s[idx]==r["current"]
            if not hit:
                # find
                where=[i for i,x in enumerate(s) if x==r["current"]]
                print("  gid",r["gid"],"seg",r["seg"],"MATCH-AT",where,"len",len(r["current"]))
    print("done")
