import io, sys, os
sys.stdout.reconfigure(encoding="utf-8")
p=r"AI語譯\out\02_戒疏\15a_卷三下之三.txt"
txt=io.open(p,encoding="utf-8").read().replace("\r\n","\n")
bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
print("block137 repr:", repr(bl[136][:70]))
print("has newline:", "\n" in bl[136])
