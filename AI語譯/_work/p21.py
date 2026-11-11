import json,sys,os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
rows=json.load(open(r"AI語譯\_work\rows_final.json",encoding="utf-8"))
for i,(k,loc,st,chg) in enumerate(rows,1):
    print(f'{i}\t{k}\t{loc}\t{st}\t{chg}')
