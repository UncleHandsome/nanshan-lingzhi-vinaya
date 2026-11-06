import json, os, re

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
src = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\03_四分律刪補隨機羯磨疏_句讀_v3.txt"
v3 = open(src, encoding="utf-8").read()

ALLOWED = set("\uff0c\u3002\u3001\uff1b\uff1a\uff1f\uff01\u300c\u300d\uff08\uff09")
WS = set("\u3000 \n\r\t")
DROP = set("\u3010\u3011\u3008\u3009\u00b7\u25cb\u2014\u2026*=-#/`[]_.")

def ignorable(c):
    return c in WS or c in ALLOWED or c in DROP or c in "\u300a\u300b\u201c\u201d\u2018\u2019"

def norm(s):
    return "".join(c for c in s if not ignorable(c))

chars = []
idx = []
for i, c in enumerate(v3):
    if not ignorable(c):
        chars.append(c); idx.append(i)
sv3 = "".join(chars)

def clean(cand):
    cand = cand.strip("\u3000 \n\r\t")
    out = []
    for c in cand:
        if c in ALLOWED:
            out.append(c)
        elif c == "\u300a":
            out.append("\u300c")
        elif c == "\u300b":
            out.append("\u300d")
        elif c in WS:
            continue
        elif c in DROP or c in "\u201c\u201d\u2018\u2019":
            continue
        else:
            out.append(c)
    return "".join(out)

inp = json.load(open(os.path.join(base, "ys_punct_in.json"), encoding="utf-8"))
res = {}
miss = []
for bi, (k, paras) in enumerate(inp.items()):
    for pi, p in enumerate(paras):
        n = norm(p)
        a = sv3.find(n)
        if a < 0:
            miss.append(f"{bi}.{pi}")
            continue
        b = a + len(n)
        cand = v3[idx[a]:idx[b-1]+1]
        res[f"{bi}.{pi}"] = clean(cand)

print("matched", len(res), "miss", len(miss))
print("miss ids:", " ".join(miss))
json.dump(res, open(os.path.join(base, "punct_work", "v3_extract.json"), "w", encoding="utf-8"), ensure_ascii=False)
