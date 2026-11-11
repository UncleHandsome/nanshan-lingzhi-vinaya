import re,sys
sys.stdout.reconfigure(encoding="utf-8")
p=r"存疑材料\complex_存疑\re3.txt"
t=open(p,encoding="utf-8").read().replace("\r\n","\n")
hs=re.findall(r'(?m)^### .*$',t)
import collections
print("lines",t.count("\n")+1,"headers",len(hs))
print(collections.Counter(h.split("｜")[1] if "｜" in h else "?" for h in hs))
for h in hs: print(h)
