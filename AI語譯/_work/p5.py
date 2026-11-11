import re, glob, os, sys, json
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
blocks=[]
for f in sorted(glob.glob(r"存疑材料\complex_存疑\complex_*.md")):
    txt=open(f,encoding="utf-8").read().replace("\r\n","\n")
    for m in re.finditer(r'(?m)^【存疑\s*([^】]+)】\s*([^/\s]+)/([^#\s]+)#(\d+)\s*$([\s\S]*?)(?=^【存疑 |\Z)', txt):
        key=m.group(1).strip(); book=m.group(2); chunk=m.group(3); para=int(m.group(4)); body=m.group(5)
        def grab(tag):
            mm=re.search(r'【'+tag+r'】([\s\S]*?)(?=\n【[^】]+】|\Z)', body)
            return mm.group(1).strip() if mm else None
        blocks.append(dict(mdfile=os.path.basename(f),key=key,book=book,chunk=chunk,para=para,
                           orig=grab("原文"),trans=grab("譯文"),doubt=grab("疑點")))
print("blocks:",len(blocks))
print("unique keys:",len({b["key"] for b in blocks}))
json.dump(blocks, open(r"AI語譯\_work\blocks.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
# report
for b in blocks[:3]:
    print(b["key"], b["book"], b["chunk"], b["para"], len(b["orig"] or ""), len(b["trans"] or ""), len(b["doubt"] or ""))
