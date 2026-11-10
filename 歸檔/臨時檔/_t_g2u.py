import sys, json
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
for i in [136,148,149,150,151,156,161,164]:
    r=rows[i]
    print(f"### row{i} {r[2]} s{r[3]} {r[4]}/{r[5]}")
    print("  O:",r[8])
    print("  P:",r[6])
    print("  S:",r[7])
    print()
