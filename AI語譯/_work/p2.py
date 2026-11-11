import re, json, os, sys
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
out=[]
for src in ["return.txt","re2.txt"]:
    txt=open(r"存疑材料\complex_存疑\\"+src,encoding="utf-8").read().replace("\r\n","\n")
    # split on header lines
    parts = re.split(r'(?m)^### ', txt)
    for p in parts[1:]:
        lines = p.split("\n")
        header = lines[0].strip()
        body = "\n".join(lines[1:])
        m = re.match(r'^(.+?)\s*｜\s*(是錯|不是錯|材料不足)(.*)$', header)
        if not m:
            out.append({"src":src,"header":header,"key":None,"verdict":"PARSE_FAIL","body":body})
            continue
        key = m.group(1).strip()
        verdict = m.group(2)
        rest = m.group(3).strip()
        # extract 判斷 and 建議
        jud=body; sug=None
        if "建議：" in body:
            i = body.index("建議：")
            jud = body[:i]
            sug = body[i+len("建議："):]
        jud = jud.strip()
        jud = re.sub(r'^判斷：','',jud).strip()
        if sug is not None:
            sug = sug.strip()
        out.append({"src":src,"key":key,"verdict":verdict,"tag":rest,"judge":jud,"sug":sug})
json.dump(out, open(r"AI語譯\_work\parsed.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
yes=[e for e in out if e["verdict"]=="是錯"]
print("entries:",len(out),"是錯:",len(yes))
# key uniqueness
import collections
c=collections.Counter(e["key"] for e in yes if e["key"])
print("dup keys among 是錯:", {k:v for k,v in c.items() if v>1})
# how many have 建議
print("有建議:", sum(1 for e in yes if e["sug"]))
print("無建議 keys:", [ (e['key'],e['src']) for e in yes if not e['sug']])
