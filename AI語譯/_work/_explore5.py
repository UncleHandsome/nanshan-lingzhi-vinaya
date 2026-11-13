import json,os
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
for fn in ["blocks.json","para_counts.json","hebian_sections.json"]:
    p=os.path.join(root,fn)
    d=json.load(open(p,encoding="utf-8"))
    print("==",fn,type(d).__name__, len(d) if hasattr(d,"__len__") else "")
    if isinstance(d,dict):
        for k in list(d)[:6]:
            v=d[k]; print("  key:",k,"->",type(v).__name__, (len(v) if hasattr(v,"__len__") else v))
            if isinstance(v,list) and v: print("     item0:",json.dumps(v[0],ensure_ascii=False)[:300])
            elif isinstance(v,dict): print("     sub:",json.dumps(v,ensure_ascii=False)[:300])
    elif isinstance(d,list):
        print("  item0:",json.dumps(d[0],ensure_ascii=False)[:400])
