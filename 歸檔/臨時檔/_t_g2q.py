import sys, json
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
res=json.load(open("_g2auto2.json",encoding="utf-8"))
for i,ch,seg,A,B in res:
    print(f"--- row{i} {ch} seg{seg} cls={rows[i][5]}")
    print("  A:",A)
    print("  B:",B)
