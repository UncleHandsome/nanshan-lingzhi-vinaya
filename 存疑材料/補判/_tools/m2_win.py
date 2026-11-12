import json, os, difflib
rows = json.load(open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), encoding="utf-8"))
for r in rows:
    if r["id"] in ("1525-0001", "1503-0001"):
        a, b = r["cur"], r["sug"]
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
        i1 = ops[0][1]; i2 = ops[-1][2]
        print("=" * 60); print(r["id"], "changed region cur[%d:%d]" % (i1, i2))
        print("CUR:", a[max(0,i1-120):i2+120])
        j1 = ops[0][3]; j2 = ops[-1][4]
        print("SUG:", b[max(0,j1-120):j2+120])
