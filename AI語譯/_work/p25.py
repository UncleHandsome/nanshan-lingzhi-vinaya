import json,sys,os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
p=r"AI語譯\out\01_行事鈔\09c_卷下之一.txt"
raw=open(p,encoding="utf-8",newline="").read(); L=raw.split("\n")
print(L[0][:400])
