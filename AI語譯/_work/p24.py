import json,sys,os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
w=json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8"))
for r in w:
    if r["base"]=="208-0001":
        print(r["cur"])
        print()
        print("[SUG]",r["sug"])
