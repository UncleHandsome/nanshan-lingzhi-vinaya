import sys
sys.stdout.reconfigure(encoding="utf-8")
p=r"存疑材料\complex_存疑\待議_套用.md"
s=open(p,encoding="utf-8",newline="").read().replace("\r\n","\n").replace("\n","\r\n")
open(p,"w",encoding="utf-8",newline="").write(s)
b=open(p,"rb").read(); print("CRLF",b.count(b"\r\n"),"LF",b.count(b"\n"))
# 最終再驗一次全部檔案
