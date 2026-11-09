# -*- coding: utf-8 -*-
import json, re, os
W = r"AI語譯/_work/review/_fixwork"
src = open(os.path.join(W, "final.py"), encoding="utf-8").read()
start = src.index("MAN = {")
m = re.search(r"^\}$", src[start:], re.M)
end = start + m.end()
block = src[start:end]
g = {}
exec(block, g)
MAN = g["MAN"]
MAN["221"] = [["END", "\u300d"]]
MAN[221] = MAN.pop("221")
MAN[126] = [["LEAD", "\uff09"]]
json.dump(MAN, open(os.path.join(W, "man.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("manual rows:", len(MAN))
print("221:", MAN[221])
