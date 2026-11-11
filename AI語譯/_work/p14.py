import json,sys,os,difflib
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
w=json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8"))
for r in w:
    if r["base"] in ("05a_卷中之一-11","111-0001","123-0001","259-0001","278-0004","484-0002") and r["cls"]!="SAME":
        print("=== ",r["base"], r["book"],r["chunk"],"#",r["found"], r["cls"], round(r["ratio"],3), r["src"], r["key"])
        print("[CUR]",r["cur"])
        print()
        print("[SUG]",r["sug"])
        print()
