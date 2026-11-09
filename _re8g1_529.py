import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
for x in d:
    if x["gid"]=="529-0005":
        print(x["seg"],x["cls"]); print("P:",x["P"]); print("S:",x["S"]); print("CUR:",x["CUR"]); print()
