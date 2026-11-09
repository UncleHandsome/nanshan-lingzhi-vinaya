import csv, sys, json
sys.stdout.reconfigure(encoding="utf-8")
p = r"AI語譯\_work\review\report_re8.tsv"
with open(p, encoding="utf-8", newline="") as fh:
    rd = csv.reader(fh, delimiter="\t"); next(rd)
    rows=[r for r in rd if r[1]=="04_比丘尼鈔"]
order={'01a_卷上之上':0,'01b_卷上之上':1,'02a_卷上之下':2,'02b_卷上之下':3,'03a_卷中之上':4,'03b_卷中之上':5,'04a_卷中之下':6,'04b_卷中之下':7}
rows.sort(key=lambda r:(order[r[2]], int(r[3]), r[0]))
json.dump(rows, open("_g2rows.json","w",encoding="utf-8"), ensure_ascii=False)
for i,r in enumerate(rows[:12]):
    print(f"### {i} gid={r[0]} {r[2]} seg{r[3]} {r[4]} {r[5]}")
    print("PROB:", r[6])
    print("SUG :", r[7])
    print("ORIG:", r[8])
    print("CUR :", r[9])
    print()
