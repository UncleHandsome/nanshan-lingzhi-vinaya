import sys, json
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
auto=[x for x in json.load(open("_g2auto.json",encoding="utf-8")) if x[3]=="APPLY"]
print(len(auto))
for i,ch,seg,st,A,B in auto:
    flags=""
    if "……" in B: flags+="[ELL]"
    if "或" in B: flags+="[HUO]"
    if B.endswith("。"): flags+="[PERIOD]"
    if "（" in B: flags+="[PAREN]"
    print(f"{i} {ch} s{seg} {flags} L={rows[i][4]}/{rows[i][5]}")
    print("   A:",A)
    print("   B:",B)
