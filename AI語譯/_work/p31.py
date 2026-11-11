import re,sys,json,os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
t=open(r"存疑材料\complex_存疑\re3.txt",encoding="utf-8").read().replace("\r\n","\n")
for p in re.split(r'(?m)^### ',t)[1:]:
    lines=p.split("\n"); h=lines[0].strip()
    if "是錯" not in h: continue
    print("=========",h)
    print("\n".join(lines[1:]))
