import json, os, re
rows = json.load(open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), encoding="utf-8"))
MAT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def rd(p):
    with open(p, encoding="utf-8-sig") as f: return f.read().replace("\r\n", "\n")
txt = rd(os.path.join(MAT, "新_補_14.md"))
i = txt.find("1525-0001")
seg = txt[i:i+200]
print(seg)
for m in re.finditer(r"直言知[^。]{0,80}", txt):
    print("HIT:", m.group(0))
