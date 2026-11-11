import json,sys,os,re
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
w=json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8"))
def show(base,kws,win=90):
    for r in w:
        if r["base"]==base:
            cur=r["cur"]
            print(f'--- {base} {r["book"]}/{r["chunk"]}#{r["found"]} cls={r["cls"]}')
            for kw in kws:
                for m in re.finditer(re.escape(kw),cur):
                    s=max(0,m.start()-win); e=min(len(cur),m.end()+win)
                    print(f'  [{kw}] …{cur[s:e]}…')
                    break
            print()
show("299-0004",["重物","貴重","記文"])
show("389-0001",["篇字","篇","記文"])
show("432-0001",["借喻","毒龍","神珠","房戒"])
show("560-0013",["南北","時政","後魏"])
show("08b_卷中之四-06",["下行","沙彌上","布薩"])
