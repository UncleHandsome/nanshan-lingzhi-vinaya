import os,sys,json
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
for p in [r"AI語譯\out\02_戒疏\03a_卷一下之一.txt", r"AI語譯\out\01_行事鈔\02a_卷上之二.txt", r"AI語譯\out\02_戒疏\09b_卷二下之二.txt"]:
    raw=open(p,encoding="utf-8",newline="").read()
    print(p, "len",len(raw), "CRLF",raw.count("\r\n"), "LF",raw.count("\n"), "splitCRLF",len(raw.split("\r\n")), "splitLF",len(raw.split("\n")))
