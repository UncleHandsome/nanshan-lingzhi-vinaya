import json,sys,os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
w=json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8"))
for r in w:
    if r["base"]=="05a_卷中之一-11":
        for k,tag in (("cur","CUR"),("sug","SUG")):
            t=r[k]; i=t.find("波藥")
            print(tag, "…", t[max(0,i-80):i+120], "…")
        print()
