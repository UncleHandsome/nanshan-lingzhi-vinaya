import json, re
from collections import Counter

out = json.load(open("AI語譯/_work/review/_jb2.json", encoding="utf-8"))
print("rows", len(out), "sum len cur", sum(x["len"] for x in out))
print("avg", sum(x["len"] for x in out)//len(out))

# tier A: 1 pair present
A = [x for x in out if x["npair"] == 1 and x["pairs_in"] == 1]
B = [x for x in out if x["npair"] >= 1 and x["pairs_in"] == 0]
C = [x for x in out if x["npair"] == 0]
print("A", len(A), "B", len(B), "C", len(C))

# A: check occurrences of old phrase, alternatives in B
multi = [x for x in A if x["cur"].count(x["pairs"][0][0]) > 1]
print("A multi-occur", len(multi))
alt = [x for x in A if re.search(r"（或[:：]", x["pairs"][0][1])]
print("A B-has-或者", len(alt))
for x in A[:3]:
    print("----")
    print("A:", x["pairs"][0][0])
    print("B:", x["pairs"][0][1])

json.dump({"A": A, "B": B, "C": C}, open("AI語譯/_work/review/_tiers.json", "w", encoding="utf-8"), ensure_ascii=False)

# B detail
with open("AI語譯/_work/review/_tierB.txt", "w", encoding="utf-8") as f:
    for x in B:
        f.write(f"=== [{x['i']}] {x['chunk']} seg{x['seg']} len={x['len']}\nSUG: {x['sug']}\n")
        for a, b in x["pairs"]:
            f.write(f"A: {a}\nB: {b}\n")
        f.write("CUR: " + x["cur"] + "\n\n")

with open("AI語譯/_work/review/_tierA_sample.txt", "w", encoding="utf-8") as f:
    for x in A[:15]:
        f.write(f"=== [{x['i']}] {x['chunk']} seg{x['seg']}\nSUG: {x['sug']}\nCUR: {x['cur']}\n\n")
