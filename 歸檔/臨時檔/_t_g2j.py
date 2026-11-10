import sys, json, io, os
sys.stdout.reconfigure(encoding="utf-8")
keep=json.load(open("_g2keep.json",encoding="utf-8"))
rows=json.load(open("_g2rows.json",encoding="utf-8"))
base=r"AI語譯\out\04_比丘尼鈔"
def blocks(ch):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read()
    txt=txt.replace("\r\n","\n")
    return [b.strip() for b in txt.split("\n\n") if b.strip()]
segs={}
for r in rows:
    segs.setdefault((r[2],r[3]), r[9])
mis=0
for (ch,s),cur in sorted(segs.items(), key=lambda kv:(kv[0][0],int(kv[0][1]))):
    bl=blocks(ch)
    idx=int(s)
    hit=[i for i,b in enumerate(bl) if b==cur]
    if hit:
        print(f"OK {ch} seg{s} -> block {hit}  (nblocks={len(bl)})")
    else:
        # try prefix/fuzzy
        near=[(i,len(b), b==cur) for i,b in enumerate(bl)]
        cand=[i for i,b in enumerate(bl) if b.startswith(cur[:40])]
        print(f"MISS {ch} seg{s} nblocks={len(bl)} cand40={cand} len={len(cur)}")
        mis+=1
print("miss",mis, "of", len(segs))
