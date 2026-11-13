import sys,os,re
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
from docx import Document
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
p=os.path.join(root,"白話","會本_篇13_篇聚名報.docx")
d=Document(p)
seq=[]
for x in d.paragraphs:
    t=x.text.strip()
    if not t: continue
    m=re.match(r"^【(鈔|記)(\d+)(?:】|（)",t)
    if m: seq.append((m.group(1),int(m.group(2)),t))
print("tagged blocks:",len(seq))
cao=[s for s in seq if s[0]=="鈔"]; ji=[s for s in seq if s[0]=="記"]
print("鈔:",len(cao),"記:",len(ji))
# 記 numbering continuity
nums=[s[1] for s in ji]
print("記 num range",min(nums),max(nums),"unique",len(set(nums)))
print("order sample:", [f"{s[0]}{s[1]}" for s in seq[:30]])
# locate each 記 block in 資持記 files
import glob
files=sorted(glob.glob(os.path.join(root,"TXT","資持記","*.txt")))[:16]
big=""
for f in files:
    big+=open(f,encoding="utf-8").read()
def nz(s): return "".join(re.findall(r"[\u4e00-\u9fff]",s))
bn=nz(big)
ok=0; miss=[]
for k,num,t in ji:
    body=re.sub(r"^【記\d+】(?:（[^）]*）)?","",t)
    key=nz(body)[:14]
    if key and key in bn: ok+=1
    else: miss.append((num,key))
print("記 blocks locatable by 14-gram prefix:",ok,"/",len(ji))
for m in miss[:5]: print("  miss",m)
