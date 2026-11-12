import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
all_e = json.load(open(os.path.join(HERE, "m1_all.json"), encoding="utf-8"))
for f in ("新_補_06_回2.txt", "新_補_08_回2.txt"):
    print("==", f)
    for e in all_e:
        if e["file"] == f:
            print("  ", e["id"], e["verdict"])
