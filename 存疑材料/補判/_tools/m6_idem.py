import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
rows = json.load(open(os.path.join(HERE, "m2_rows.json"), encoding="utf-8"))
POST = {"1525-0001": [("而非從見聞而來", "而非從眼見耳聞而來")]}
cnt = collections.Counter()
changed = 0
for r in rows:
    lines = open(r["file"], encoding="utf-8-sig", newline="").read().split("\n")
    nz = [i for i, l in enumerate(lines) if l.strip()]
    cur = lines[nz[r["seg"]-1]].rstrip("\r")
    want = r["sug"]
    for a, b in POST.get(r["id"], []):
        want = want.replace(a, b)
    if cur == want:
        cnt["已相符"] += 1
    else:
        cnt["仍不同"] += 1
        print("DIFF", r["id"])
print(cnt)
