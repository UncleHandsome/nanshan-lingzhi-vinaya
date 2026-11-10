import sys, json, io
sys.stdout.reconfigure(encoding="utf-8")
keep=json.load(open("_g2keep.json",encoding="utf-8"))
target=sys.argv[1]
out=[]
segs={}
for i,r in keep:
    if r[2]!=target: continue
    segs.setdefault(r[3], []).append((i,r))
def sk(s):
    try: return int(s)
    except: return 999
for seg in sorted(segs, key=sk):
    items=segs[seg]
    cur=items[0][1][9]
    out.append(f"===== {target} seg{seg}  rows={[i for i,_ in items]}  len={len(cur)}")
    for i,r in items:
        out.append(f"-- row{i} {r[4]} {r[5]} gid={r[0]}")
        out.append("   P: "+r[6])
        out.append("   S: "+r[7])
        out.append("   O: "+r[8])
    out.append("--- CURRENT:")
    out.append(cur)
    out.append("")
io.open(f"_g2v_{target[:3]}.txt","w",encoding="utf-8").write("\n".join(out))
print("wrote", f"_g2v_{target[:3]}.txt", len("\n".join(out)))
