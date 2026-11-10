import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
for x in d:
    if x["gid"] in ("455-0009","517-0021") or (x["gid"]=="516-0007"):
        print("##",x["gid"],x["seg"],x["cls"])
        print("  P:",x["P"][:160])
        print("  S:",x["S"])
        print("  PAIRS:",x["pairs"])
        print()
