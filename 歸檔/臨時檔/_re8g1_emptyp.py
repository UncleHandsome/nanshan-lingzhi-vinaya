import json
g=json.load(open(r"AI語譯\_work\review\_re8g1_rows.json",encoding="utf-8"))
for r in g:
    if r[1]=="03_業疏" and not r[6].strip():
        print(r[0],r[2],r[3],r[4],r[5])
        print("  S:",r[7])
