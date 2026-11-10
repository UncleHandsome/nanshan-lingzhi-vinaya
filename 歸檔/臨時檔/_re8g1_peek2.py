import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
want={"466-0017","482-0024","517-0017","517-0018","523-0009","507-0010","511-0015"}
out=[]
for x in d:
    if x["gid"] in want:
        out.append(f'### {x["gid"]} seg={x["seg"]} {x["cls"]}')
        out.append(f'S: {x["S"]}')
        out.append(f'CUR: {x["CUR"]}')
        out.append("")
open(r"AI語譯\_work\review\_peek2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
