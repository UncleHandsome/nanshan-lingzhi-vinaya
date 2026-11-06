import json, os, re

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
work = os.path.join(base, "punct_work")
MARKS = "\uff0c\u3002\u3001\uff1b\uff1a\uff1f\uff01\u300c\u300d\uff08\uff09"
MSET = set(MARKS)

inp = json.load(open(os.path.join(base, "ys_punct_in.json"), encoding="utf-8"))
draft = json.load(open(os.path.join(work, "draft.json"), encoding="utf-8"))
keys = list(inp.keys())

def strip(s):
    return "".join(c for c in s if c not in MSET)

rep = []
bad = 0
brackets = 0
odd = 0
for bi, blk in enumerate(draft["blocks"]):
    k = keys[bi]
    for pi, (src, got) in enumerate(zip(inp[k], blk["texts"])):
        if strip(src) != strip(got):
            bad += 1
            rep.append(f"CHARS {bi}.{pi}")
            continue
        # insertion-only check
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
        if i != len(src) or j != len(got) or not ok:
            bad += 1
            rep.append(f"INSERT {bi}.{pi}")
        if got.count("\u300c") != got.count("\u300d"):
            brackets += 1
            rep.append(f"QUOTE {bi}.{pi} {got.count(chr(0x300c))}/{got.count(chr(0x300d))}")
        if got.count("\uff08") != got.count("\uff09"):
            brackets += 1
            rep.append(f"PAREN {bi}.{pi}")
        if re.search(r"[\uff0c\u3001\uff1b\uff1a][\u3002\uff0c\u3001\uff1b\uff1a]", got) or re.search(r"\u3002[\uff0c\u3001\uff1b\uff1a]", got) or "，，" in got or "。。" in got:
            odd += 1
            rep.append(f"ODD {bi}.{pi} {got[:0]}")
        if got.startswith(tuple("\uff0c\u3001\uff1b\uff1a\u300d\uff09\u3002")):
            odd += 1
            rep.append(f"START {bi}.{pi}")
        if len(got) and inp[k][pi].rstrip().endswith("\u3002") and not got.endswith(("\u3002", "\uff01", "\uff1f", "\u300d")):
            rep.append(f"NOEND {bi}.{pi}")

print("bad", bad, "bracket_issues", brackets, "odd", odd, "total_notes", len(rep))
open(os.path.join(work, "verify.txt"), "w", encoding="utf-8").write("\n".join(rep))
