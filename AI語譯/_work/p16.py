import json,sys,os,re
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
w=json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8"))
p=json.load(open(r"AI語譯\_work\parsed2.json",encoding="utf-8"))
for e in p:
    if e["verdict"]=="是錯" and e["key"].startswith("044-0001"):
        print("### 044-0001 判斷:",e["judge"]); print("SUG:",e["sug"][:200],"..."); print()
for r in w:
    if r["base"]=="05a_卷中之一-11":
        print("[CUR]"); i=r["cur"].find("波逸提"); print(r["cur"][max(0,i-60):i+160])
        print(); print("[SUG]"); j=r["sug"].find("波逸提"); print(r["sug"][max(0,j-60):j+160])
