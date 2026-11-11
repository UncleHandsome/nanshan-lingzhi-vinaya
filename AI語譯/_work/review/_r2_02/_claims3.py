# -*- coding: utf-8 -*-
"""Item-level claim extraction: heading(+ID) + body => one claim. Tables => per-row claims."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L

ID_FULL=re.compile(r"(?<!\d)(\d{3})-(\d{4})(?!\d)")
NEG=re.compile(r"無誤|無問題|正確|妥當|無需|不必|不需|均可|皆可|無礙|允當|貼切|精準|未見問題|沒有問題|無須|可以不改|未見")
CLAIM=re.compile(r"問題|建議|應作|宜作|宜改|改為|改作|誤|漏|增譯|脫|應是|不當|不符|矛盾|相反|顛倒|生硬|可作|不妥|欠|缺|錯|混|失|費解|難懂|不統一|不一致|歧義|贅|多餘|語病|搭配|不通|未譯|查無|無據")
SUMMARY=re.compile(r"最該改|總計|總結|優先|以上所|合計|總共|先改")
HEAD=re.compile(r"^(#{1,6}\s|\*\*|\d+[.、]\s*\*\*|\d+[.、]\s*【)")

def resp_nums():
    d=os.path.join(ROOT,"batch_qwen","r2"); out=[]
    for f in os.listdir(d):
        m=re.match(r"resp_(\d+)\.txt$",f)
        if m and 550<=int(m.group(1))<=641: out.append(int(m.group(1)))
    return sorted(out)

def find_ids(txt, pre, idx, budget=None):
    out=[]
    for m in ID_FULL.finditer(txt):
        g=m.group(1)+"-"+m.group(2)
        if g in idx and g not in out: out.append(g)
    if not out:
        for m in re.finditer(r"(?<!\d)(\d{4})(?!\d)",txt):
            if budget is not None and m.start()>budget: continue
            g="%s-%s"%(pre,m.group(1))
            if g in idx and g not in out: out.append(g)
    return out

def parse(n, idx):
    t=io.open(os.path.join(ROOT,"batch_qwen","r2","resp_%d.txt"%n),encoding="utf-8-sig").read()
    lines=t.split("\n")
    claims=[]
    item={"ids":[],"head":"","body":[],"start":0}
    def flush():
        if not item["ids"]: return
        txt=re.sub(r"\s+"," "," ".join([item["head"]]+item["body"])).strip()
        if len(txt)<10: return
        claims.append({"resp":n,"ln":item["start"],"ids":item["ids"],"text":txt,
                       "head":item["head"][:70],"summ":bool(SUMMARY.search(item["head"][:40]))})
    i=0
    while i<len(lines):
        s=lines[i].strip()
        if not s: i+=1; continue
        if s.startswith("|"):
            rows=[]; j=i
            while j<len(lines) and lines[j].strip().startswith("|"):
                rows.append(lines[j].strip()); j+=1
            body=[r for r in rows if not re.match(r"^\|[\s\-:|]+\|?$",r)]
            if body and re.search(r"原譯|問題／|建議\s*\|",body[0]): body=body[1:]
            for r in body:
                rid=find_ids(r,n,idx,budget=20)
                ids=rid or item["ids"]
                if not ids: continue
                claims.append({"resp":n,"ln":j,"ids":ids,"text":re.sub(r"\s+"," ",r).strip(),
                               "head":"","summ":bool(SUMMARY.search(r[:40]))})
            i=j; continue
        if HEAD.match(s):
            ids=find_ids(s,n,idx,budget=90)
            flush()
            if ids:
                item={"ids":ids,"head":s,"body":[],"start":i}
            else:
                # sub-heading: keep parent ids if it's a subsection (#### or bold), else close
                if s.startswith("####") or s.startswith("**") or re.match(r"^\d+[.、]",s):
                    item={"ids":item["ids"],"head":item["head"],"body":[],"start":i}
                else:
                    item={"ids":[],"head":"","body":[],"start":i}
            i+=1; continue
        item["body"].append(s); i+=1
    flush()
    return claims

def main():
    idx=L.load_map()["idx"]
    allc=[]
    for n in resp_nums(): allc.extend(parse(n,idx))
    keep=[]
    for c in allc:
        t=c["text"]
        if not CLAIM.search(t): continue
        if NEG.search(t) and not re.search(r"建議|應作|宜改|改為|問題[:：]",t): continue
        keep.append(c)
    for i,c in enumerate(keep): c["cid"]="K%03d"%i
    json.dump(keep,io.open(os.path.join(OUT,"_claims3.json"),"w",encoding="utf-8"),ensure_ascii=False)
    ch=collections.Counter()
    for c in keep:
        for g in c["ids"]: ch[idx[g]["chunk"][:3]]+=1
    print("claims:",len(keep),"chars:",sum(len(c["text"]) for c in keep))
    print(sorted(ch.items()))
    io.open(os.path.join(OUT,"_claims3_out.txt"),"w",encoding="utf-8").write(
        "\n".join("%s r%d %s %s"%(c["cid"],c["resp"],c["ids"][:2],c["text"][:90]) for c in keep if c["resp"] in (550,570)))

if __name__=="__main__": main()
