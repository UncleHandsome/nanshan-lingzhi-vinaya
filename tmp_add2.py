# -*- coding: utf-8 -*-
import io
p=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r2_done.txt"
t=io.open(p,encoding="utf-8-sig").read()
line="02_戒疏:550-641(全)"
if line not in t:
    if not t.endswith("\n"): t+="\n"
    t+=line+"\n"
    io.open(p,"w",encoding="utf-8-sig",newline="").write(t)
    print("appended")
else:
    print("exists")
