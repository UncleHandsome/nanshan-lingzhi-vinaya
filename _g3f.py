import io, sys, os, json
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
bad=[]
for ch,seg,new in out:
    old=blocks(ch)[int(seg)-1]
    if old==new: bad.append(("NOCHANGE",ch,seg))
    if "\n" in new or "\t" in new: bad.append(("NL",ch,seg))
    for bg in ["。。","，，","；；","：：","、、","」」","「「","。，","，。","：；"]:
        if bg in new and bg not in old: bad.append((bg,ch,seg, new[max(0,new.find(bg)-15):new.find(bg)+15]))
    if new.count("「")-new.count("」") != old.count("「")-old.count("」"):
        bad.append(("QUOTE",ch,seg, old.count("「"),old.count("」"),new.count("「"),new.count("」")))
    if new.count("『")-new.count("』") != old.count("『")-old.count("』"):
        bad.append(("QUOTE2",ch,seg))
    if len(new) > len(old)*1.6: bad.append(("GROW",ch,seg,len(old),len(new)))
print("issues:", len(bad))
for b in bad: print(" ",b)
print("segments:", len(out))
