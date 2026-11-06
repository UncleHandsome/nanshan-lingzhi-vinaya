import json, os

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
work = os.path.join(base, "punct_work")
MARKS = "\uff0c\u3002\u3001\uff1b\uff1a\uff1f\uff01\u300c\u300d\uff08\uff09"
MSET = set(MARKS)

inp = json.load(open(os.path.join(base, "ys_punct_in.json"), encoding="utf-8"))
draft = json.load(open(os.path.join(work, "draft.json"), encoding="utf-8"))
keys = list(inp.keys())

END_FIX = ["1.13", "1.19", "1.21", "1.85", "1.96", "1.106", "3.9", "3.106", "3.134"]
START_FIX = ["2.25", "2.65", "2.68", "2.99", "2.100", "3.87", "3.108", "3.109"]

def get(blk, key):
    b, p = map(int, key.split("."))
    return blk[b]["texts"][p]

def put(blk, key, val):
    b, p = map(int, key.split("."))
    blk[b]["texts"][p] = val

for key in END_FIX:
    t = get(draft["blocks"], key)
    if t.endswith("\u3002"):
        t = t[:-1] + "\u300d\u3002"
    else:
        t = t + "\u300d"
    put(draft["blocks"], key, t)

for key in START_FIX:
    t = get(draft["blocks"], key)
    put(draft["blocks"], key, "\u300c" + t)

def strip(s):
    return "".join(c for c in s if c not in MSET)

bad = []
for bi, blk in enumerate(draft["blocks"]):
    k = keys[bi]
    for pi, (src, got) in enumerate(zip(inp[k], blk["texts"])):
        if strip(src) != strip(got):
            bad.append(f"CHARS {bi}.{pi}")
            continue
        i = j = 0
        ok = True
        while i < len(src) and j < len(got):
            if src[i] == got[j]:
                i += 1; j += 1
            elif got[j] in MSET:
                j += 1
            else:
                ok = False; break
        while j < len(got) and got[j] in MSET:
            j += 1
        if not ok or i != len(src) or j != len(got):
            bad.append(f"INSERT {bi}.{pi}")
        if got.count("\u300c") != got.count("\u300d"):
            bad.append(f"QUOTE {bi}.{pi}")

print("bad", len(bad), bad[:10])
if not bad:
    json.dump({"blocks": draft["blocks"]}, open(os.path.join(base, "ys_punct_out.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE ys_punct_out.json")
