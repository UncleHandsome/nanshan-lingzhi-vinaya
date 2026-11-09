import sys, json
sys.stdout.reconfigure(encoding="utf-8")
keep=json.load(open("_g2keep.json",encoding="utf-8"))
s=sum(len(r[9]) for i,r in keep)
print("rows",len(keep),"sum current",s)
segsum={}
for i,r in keep:
    k=(r[2],r[3]); segsum[k]=max(segsum.get(k,0), len(r[9]))
print("unique seg text sum", sum(segsum.values()))
