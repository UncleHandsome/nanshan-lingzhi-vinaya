import sys, json, io, os
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
base=r"AI語譯\out\04_比丘尼鈔"
def blocks(ch):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    return [b.strip() for b in txt.split("\n\n") if b.strip()]
seen={}
for i,r in enumerate(rows):
    if "重複" not in r[6]: continue
    ch,seg,cur=r[2],r[3],r[9]
    if (ch,seg) in seen: continue
    seen[(ch,seg)]=1
    bl=blocks(ch)
    cnt=sum(1 for b in bl if b==cur)
    # also check if a long substring at start repeats
    head=cur[:60]
    cnt2=sum(1 for b in bl if head and head in b)
    print(f"{ch} seg{seg} exact_blocks={cnt} head_in_blocks={cnt2}")
