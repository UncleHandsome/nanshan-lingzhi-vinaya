import sys, json
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
for i in [39,40,43,44,45,46,93,94,95,96,97,98,99,111,131,86,122,166,73,50,51,52]:
    r=rows[i]
    print(f"### row{i} {r[2]} s{r[3]} {r[4]}/{r[5]}")
    print("  O:",r[8])
    print("  P:",r[6])
    print("  S:",r[7])
