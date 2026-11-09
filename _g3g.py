import io, sys, os, json, difflib
sys.stdout.reconfigure(encoding="utf-8")
base=r"AI語譯\out\04_比丘尼鈔"
def clean(s): return s.replace("\r","").replace("\n","").replace("\t","").strip()
_cache={}
def blocks(ch):
    if ch not in _cache:
        txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
        _cache[ch]=[clean(b) for b in txt.split("\n\n") if b.strip()]
    return _cache[ch]
out=json.load(open("_g2out.json",encoding="utf-8"))
lines=[]
for ch,seg,new in out:
    old=blocks(ch)[int(seg)-1]
    sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
    ops=[o for o in sm.get_opcodes() if o[0]!="equal"]
    lines.append(f"== {ch} seg{seg} len{len(old)}->{len(new)} hunks={len(ops)}")
    for tag,i1,i2,j1,j2 in ops:
        pre=old[max(0,i1-18):i1]; post=old[i2:i2+18]
        lines.append(f"   [{pre}] <<{old[i1:i2]}>> → <<{new[j1:j2]}>> [{post}]")
io.open("_g3diff.txt","w",encoding="utf-8").write("\n".join(lines))
print("lines", len(lines))
