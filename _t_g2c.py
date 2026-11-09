import csv, sys, json
sys.stdout.reconfigure(encoding="utf-8")
p = r"AI語譯\_work\review\report_re8.tsv"
rows=[]
with open(p, encoding="utf-8", newline="") as fh:
    rd = csv.reader(fh, delimiter="\t"); next(rd)
    rows=[r for r in rd if r[1]=="04_比丘尼鈔"]
lens=[len(r[9]) for r in rows]
print("current len: min",min(lens),"max",max(lens),"sum",sum(lens))
plens=[len(r[6]) for r in rows]
print("problem len: sum",sum(plens),"max",max(plens))
slens=[len(r[7]) for r in rows]
print("sugg len: sum",sum(slens),"max",max(slens))
olens=[len(r[8]) for r in rows]
print("orig len: sum",sum(olens),"max",max(olens))
# how many rows have orig present
print("orig present", sum(1 for r in rows if r[8].strip()))
