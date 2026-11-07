import json, sys
rows = json.load(open(r"AI語譯\_work\review\_g3_rows.json", encoding="utf-8"))
a, b = int(sys.argv[1]), int(sys.argv[2])
for i in range(a, b):
    r = rows[i]
    print(f"===== [{i}] {r['book']} {r['chunk']} seg{r['seg']} {r['level']}")
    print(f"CLS: {r['cls']}")
    print(f"PROBLEM: {r['problem']}")
    print(f"SUGGESTION: {r['suggestion']}")
    print(f"ORIG: {r['orig']}")
    print(f"CURRENT: {r['current']}")
    print()
