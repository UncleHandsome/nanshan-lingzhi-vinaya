import json, re

out = json.load(open("AI語譯/_work/review/_jb2.json", encoding="utf-8"))

def norm(s):
    return s.replace("『", "「").replace("』", "」")

mech, fail, nopair = [], [], []
for x in out:
    if x["npair"] == 0:
        nopair.append(x); continue
    ok = True
    for a, b in x["pairs"]:
        if not (a in x["cur"] or norm(a) in x["cur"]):
            ok = False
    (mech if ok else fail).append(x)

print("mech", len(mech), "fail", len(fail), "nopair", len(nopair))

# alternatives in B
alts = [x for x in mech for a, b in x["pairs"] if re.search(r"（或[:：]", b) or "或「" in b]
print("B with alternatives:", len(alts))
for x in alts:
    for a, b in x["pairs"]:
        print("[%d] B:" % x["i"], b)

# multi-occur check
multi = []
for x in mech:
    for a, b in x["pairs"]:
        na = norm(a)
        if x["cur"].count(a) > 1 or x["cur"].count(na) > 1:
            multi.append((x["i"], a, x["cur"].count(a), x["cur"].count(na)))
print("multi-occur:", multi)

# dump mech pairs
with open("AI語譯/_work/review/_mech.txt", "w", encoding="utf-8") as f:
    for x in mech:
        f.write(f"[{x['i']}] {x['seg']}\n")
        for a, b in x["pairs"]:
            f.write("  - " + a + "\n  + " + b + "\n")

# dump nopair rows for manual
with open("AI語譯/_work/review/_nopair.txt", "w", encoding="utf-8") as f:
    for x in nopair:
        f.write(f"=== [{x['i']}] {x['chunk']} seg{x['seg']} len={x['len']}\nSUG: {x['sug']}\nCUR: {x['cur']}\n\n")
