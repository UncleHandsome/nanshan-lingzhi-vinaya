import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
for x in d:
    if x["chunk"] in ("14b_卷三之三","06b_卷一之六") and x["seg"] in ("97","18"):
        print("###",x["gid"],x["chunk"],x["seg"],x["cls"])
        print("P:",x["P"])
        print("S:",x["S"])
        print("CUR:",x["CUR"])
        print("PAIRS:",x["pairs"])
        print()
