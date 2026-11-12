import json, os
rows = json.load(open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), encoding="utf-8"))
r = [x for x in rows if x["id"] == "1525-0001"][0]
a, b = r["cur"], r["sug"]
print("CUR 4680-4860:", a[4680:4860])
print()
print("SUG 4680-4860:", b[4680:4860])
print()
print("len a,b", len(a), len(b))
