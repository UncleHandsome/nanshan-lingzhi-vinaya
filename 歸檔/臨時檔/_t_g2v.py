import sys, json
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
for i in [41,42,54,55,58,60,72,84,89,103,104,111,115,119,127,137,140,141,143,144,146,147,154,155,157,158,159,166,167,168,169,170,171,172]:
    r=rows[i]
    print(f"### row{i} {r[2]} s{r[3]} {r[4]}/{r[5]}  O:{r[8]}")
    print("  P:",r[6])
