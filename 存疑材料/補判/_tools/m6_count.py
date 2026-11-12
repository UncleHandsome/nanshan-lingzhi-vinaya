import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
all_e = json.load(open(os.path.join(HERE, "m1_all.json"), encoding="utf-8"))
print("total", len(all_e))
print(collections.Counter(e["verdict"] for e in all_e))
print("files used:", len(set(e["file"] for e in all_e)))
for f, c in collections.Counter(e["file"] for e in all_e).items():
    print(" ", f, c, collections.Counter(e["verdict"] for e in all_e if e["file"] == f))
