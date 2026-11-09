import io, sys, json, os
sys.stdout.reconfigure(encoding="utf-8")
p=r"AI語譯\_work\review\fix_re8_g2.tsv"
raw=io.open(p,encoding="utf-8",newline="").read()
lines=raw.split("\n")
data=[l for l in lines if l.strip()]
print("lines:", len(data), "trailing newline:", raw.endswith("\n"))
import collections
print("fieldcounts:", collections.Counter(len(l.split("\t")) for l in data))
print("books:", collections.Counter(l.split("\t")[0] for l in data))
keys=[(l.split("\t")[1], int(l.split("\t")[2])) for l in data]
print("dup keys:", len(keys)-len(set(keys)))
print("min/max len:", min(len(l.split("\t")[3]) for l in data), max(len(l.split("\t")[3]) for l in data))
print("empty new:", sum(1 for l in data if not l.split("\t")[3].strip()))
# ensure every seg is within live block range and new != base
base=r"AI語譯\out\04_比丘尼鈔"
def clean(s): return s.replace("\r","").replace("\n","").replace("\t","").strip()
cache={}
def blocks(ch):
    if ch not in cache:
        txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
        cache[ch]=[clean(b) for b in txt.split("\n\n") if b.strip()]
    return cache[ch]
same=0
for l in data:
    book,ch,seg,t=l.split("\t")
    b=blocks(ch)[int(seg)-1]
    if b==t: same+=1
print("identical to base:", same)
# chunk counts
print(collections.Counter(l.split("\t")[1] for l in data))
