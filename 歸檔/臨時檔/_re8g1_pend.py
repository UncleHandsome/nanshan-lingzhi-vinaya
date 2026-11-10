import json,re
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
src=open(r"_re8g1_build.py",encoding="utf-8").read()
ns={}; exec(src.split("# group rows by segment")[0], ns)
MANUAL=ns["MANUAL"]; SKIP=ns["SKIP"]
n=0
for x in d:
    key=(x["gid"],x["seg"],x["cls"])
    if key in SKIP: continue
    edits = MANUAL[key] if key in MANUAL else x["pairs"]
    for old,new in edits:
        if old and new and old[-1] in "。？！" and new[-1] not in "。？！」":
            n+=1; print(x["gid"],x["seg"],"|",old[-20:],"|",new[-30:])
print("count",n)
