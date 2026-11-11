import io,os,re
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
D=os.path.join(ROOT,"AI語譯","out","02_戒疏")
for f in sorted(os.listdir(D)):
    if not f.endswith(".txt"): continue
    t=io.open(os.path.join(D,f),encoding="utf-8",newline="").read()
    crlf=t.count("\r\n"); lf=t.count("\n")-crlf
    print("%-28s crlf=%-5d lone_lf=%-4d endswith=%r"%(f,crlf,lf,t[-4:]))
