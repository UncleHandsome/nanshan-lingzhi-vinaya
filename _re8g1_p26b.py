import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
for x in d:
    if x["gid"]=="544-0026":
        pass
# orig not stored; reload
g=json.load(open(r"AI語譯\_work\review\_re8g1_rows.json",encoding="utf-8"))
for r in g:
    if r[0]=="544-0026":
        print("ORIG:",r[8])
        print("PROB:",repr(r[6]))
        print("SUG:",r[7])
        print()
