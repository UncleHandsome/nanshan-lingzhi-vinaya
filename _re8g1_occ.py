import json, re
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
import importlib.util
spec=importlib.util.spec_from_file_location("b", r"_re8g1_build.py")
# instead of importing (it writes), reparse manual from file
src=open(r"_re8g1_build.py",encoding="utf-8").read()
ns={}
exec(src.split("# group rows by segment")[0], ns)
MANUAL=ns["MANUAL"]; SKIP=ns["SKIP"]
cur={}
for x in d: cur[(x["chunk"],x["seg"])]=x["CUR"]
flags=[]
for x in d:
    key=(x["gid"],x["seg"],x["cls"])
    if key in SKIP: continue
    edits = MANUAL[key] if key in MANUAL else x["pairs"]
    for old,new in edits:
        c=cur[(x["chunk"],x["seg"])].count(old)
        if c!=1:
            flags.append((x["gid"],x["seg"],c,old[:50]))
print("multi-occurrence or zero edits:",len(flags))
for f in flags: print("  ",f)
