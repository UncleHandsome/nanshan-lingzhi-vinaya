import json,sys,os,difflib
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
targets=[("01_行事鈔","06a_卷中之二",6,"108-0001"),("01_行事鈔","06a_卷中之二",21,"114-0001"),("02_戒疏","01a_卷一上之一",94,"304-0016")]
for book,chunk,para,key in targets:
    e=json.load(open(rf"AI語譯\_work\re3_{key}.json",encoding="utf-8"))
    raw=open(os.path.join("AI語譯","out",book,chunk+".txt"),encoding="utf-8",newline="").read()
    L=raw.split("\n")
    cur=L[2*para-2].rstrip("\r")
    print("="*20,key,book,chunk,"#",para,"lines",len(L))
    print("[CUR]",cur)
    print()
    print("[SUG]",e["sug"])
    print()
    a=cur.strip(); b=e["sug"].strip()
    sm=difflib.SequenceMatcher(None,a,b)
    print("ratio",round(sm.ratio(),4))
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=="equal": continue
        print(f'  [{tag}] …{a[max(0,i1-30):i1]}【-{a[i1:i2]}-】【+{b[j1:j2]}+】{a[i2:i2+30]}…')
    print()
