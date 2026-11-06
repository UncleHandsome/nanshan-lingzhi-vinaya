import json, os, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
d = os.path.join("AI語譯", "_work", "align_ai")
for f in ["020", "021", "022", "023", "024"]:
    src = json.load(open(os.path.join(d, f + ".json"), encoding="utf-8"))
    try:
        out = json.load(open(os.path.join(d, "out_" + f + ".json"), encoding="utf-8"))
    except FileNotFoundError:
        print(f, "no out"); continue
    m = {x["z"]: x["c"] for x in out["map"]}
    cs = [m[x["z"]] for x in src["items"]]
    cc = [x["c"] for x in src["cand"]]
    print(f, "items", len(cs), "distinct c used", len(set(cs)), "range", min(cs), max(cs),
          "cand", min(cc), max(cc), "monotonic", cs == sorted(cs))
    print("   seq:", "".join(str(x % 10) for x in cs))
