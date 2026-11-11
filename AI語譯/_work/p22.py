import json,sys,os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
rows=json.load(open(r"AI語譯\_work\rows_final.json",encoding="utf-8"))
rows=[list(r) for r in rows]
for r in rows:
    r[3]=r[3].replace("（見 #1）","（見本表 044-0001 套用條）")
json.dump(rows,open(r"AI語譯\_work\rows_final.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
for i,(k,loc,st,chg) in enumerate(rows[39:],40):
    print(f'{i}\t{k}\t{loc}\t{st}\t{chg}')
