import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
BOOK={}
for ch in set(x["chunk"] for x in d):
    BOOK[ch]=[l.strip() for l in open(rf"AI語譯\out\03_業疏\{ch}.txt",encoding="utf-8").read().split("\n") if l.strip()]
rows=[]
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    rows.append(f)
print("rows",len(rows))
same=0; noend=0; short=0
for f in rows:
    ch,seg,txt=f[1],f[2],f[3]
    idx=int(seg)-1
    if BOOK[ch][idx]==txt: same+=1
    if not (txt.endswith("。") or txt.endswith("」") or txt.endswith("！") or txt.endswith("？")):
        noend+=1; print("NOEND",ch,seg,txt[-25:])
    if len(txt)<20: short+=1; print("SHORT",ch,seg,txt)
print("same as book:",same,"noend:",noend,"short:",short)
# check each target segment exists
for f in rows:
    if int(f[2])>len(BOOK[f[1]]): print("SEG OOR",f[1],f[2])
print("done")
