import re, os, sys, json, difflib, collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
# 1. re-parse with 建議 trailing separator stripped
out=[]
for src in ["return.txt","re2.txt"]:
    txt=open(r"存疑材料\complex_存疑\\"+src,encoding="utf-8").read().replace("\r\n","\n")
    parts=re.split(r'(?m)^### ', txt)
    for p in parts[1:]:
        lines=p.split("\n"); header=lines[0].strip(); body="\n".join(lines[1:])
        m=re.match(r'^(.+?)\s*｜\s*(是錯|不是錯|材料不足)(.*)$',header)
        if not m: continue
        key=m.group(1).strip(); verdict=m.group(2); tag=m.group(3).strip()
        jud=body; sug=None
        if "建議：" in body:
            i=body.index("建議："); jud=body[:i]; sug=body[i+3:]
        jud=re.sub(r'^判斷：','',jud.strip()).strip()
        if sug is not None:
            sug=sug.strip()
            sug=re.sub(r'\n+\s*-{3,}\s*$','',sug).strip()
            sug=re.sub(r'\n\s*-{3,}\s*\n?$','',sug).strip()
        out.append(dict(src=src,key=key,verdict=verdict,tag=tag,judge=jud,sug=sug))
json.dump(out,open(r"AI語譯\_work\parsed2.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
yes=[e for e in out if e["verdict"]=="是錯"]
print("是錯",len(yes),"有建議",sum(1 for e in yes if e["sug"]))
print("尾巴含---:",[e["key"] for e in yes if e["sug"] and "---" in e["sug"][-8:]])
blocks=json.load(open(r"AI語譯\_work\blocks.json",encoding="utf-8"))
print("blocks no trans:",sum(1 for b in blocks if not b["trans"]))
