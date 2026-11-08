import json, sys

rows = json.load(open(r"AI語譯\_work\review\_re2g1_rows.json", encoding="utf-8"))
idx = [int(x) for x in sys.argv[1:]]
for i in idx:
    r = rows[i - 1]
    print(f"===[{i}] {r['gid']} {r['chunk']} seg{r['seg']}")
    print(f"P: {r['problem']}")
    print(f"S: {r['suggestion']}")
    print(f"C: {r['current']}")
    print()
