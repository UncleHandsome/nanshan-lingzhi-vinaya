import json, os, difflib
rows = json.load(open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), encoding="utf-8"))
r = [x for x in rows if x["id"] == "1525-0001"][0]
print("JUDGE:", r["judge"])
a, b = r["cur"], r["sug"]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != "equal":
        print("-" * 40)
        print(tag, "CUR[%d:%d]=%r" % (i1, i2, a[i1:i2]), "SUG=%r" % b[j1:j2])
        print("  ctx:", a[max(0, i1-90):i2+90])
