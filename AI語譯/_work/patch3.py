import re
p=r"AI語譯\_work\mkrows.py"
s=open(p,encoding="utf-8").read()
s=s.replace('"560-0013":"return.txt",\n}', '"560-0013":"return.txt", "208-0001":"re2.txt",\n}')
s=s.replace('PENDING = {("208-0001","re2.txt")}', 'PENDING = set()')
s=s.replace('"與判斷相反，不採用（見 待議說明）"', '"與判斷相反，不採用"')
s=s.replace('𮂂果', '𮒂果')
open(p,"w",encoding="utf-8",newline="").write(s)
print("ok")
