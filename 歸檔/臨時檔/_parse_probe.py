import re, io, collections
p = r"校閱批次/new/已完成/re0/re0.txt"
txt = io.open(p, encoding="utf-8-sig").read()
lines = txt.split("\n")
# split on ### headers
items=[]; cur=None
for ln in lines:
    if ln.startswith("### "):
        if cur: items.append(cur)
        cur={"header":ln[4:].strip(),"body":[]}
    elif cur is not None:
        cur["body"].append(ln)
if cur: items.append(cur)
print("headers:", len(items))
for it in items:
    h=it["header"]
    body="\n".join(it["body"])
    if not body.strip():
        print("EMPTY-BODY:", h); continue
    if not re.match(r"^【?\d{3}-\d{4}", h):
        print("NONENTRY:", h); continue
print("---- count with fmt")
cnt=collections.Counter()
for it in items:
    h=it["header"]
    parts=h.split("｜")
    cnt[(len(parts), parts[0][:4])]+=1
print(cnt)
