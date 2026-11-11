import re,sys,json,os,difflib,collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
t=open(r"存疑材料\complex_存疑\re3.txt",encoding="utf-8").read().replace("\r\n","\n")
entries=[]
for p in re.split(r'(?m)^### ',t)[1:]:
    lines=p.split("\n"); h=lines[0].strip(); body="\n".join(lines[1:])
    m=re.match(r'^(.+?)\s*｜\s*(是錯|不是錯|材料不足)(.*)$',h)
    key=m.group(1).strip(); verdict=m.group(2)
    jud=body; sug=None
    if "建議：" in body:
        i=body.index("建議："); jud=body[:i]; sug=body[i+3:]
    jud=re.sub(r'^判斷：','',jud.strip()).strip()
    if sug is not None:
        sug=sug.strip(); sug=re.sub(r'\n+\s*-{3,}\s*$','',sug).strip()
    entries.append(dict(key=key,verdict=verdict,judge=jud,sug=sug))
json.dump(entries,open(r"AI語譯\_work\re3_parsed.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
blocks=json.load(open(r"AI語譯\_work\blocks.json",encoding="utf-8"))
bykey=collections.defaultdict(list)
for b in blocks: bykey[b["key"]].append(b)
def base(k): return re.sub(r'\s*[（(][^）)]*[）)]\s*$','',k).strip()
yes=[e for e in entries if e["verdict"]=="是錯"]
print("re3 是錯:",len(yes))
for e in yes:
    bb=None
    for cand in [e["key"], base(e["key"])]:
        if cand in bykey: bb=cand; break
    print("---",e["key"],"->",bb, bykey[bb][0]["book"]+"/"+bykey[bb][0]["chunk"]+"#"+str(bykey[bb][0]["para"]) if bb else None, "sugLen",len(e["sug"] or ""))
    json.dump(e,open(rf"AI語譯\_work\re3_{e['key']}.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
