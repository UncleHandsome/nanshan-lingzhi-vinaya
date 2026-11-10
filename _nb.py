import io
p = r"AI語譯/out/02_戒疏/02d_卷一上之二.txt"
ps=[s for s in io.open(p, encoding="utf-8").read().split("\n") if s.strip()]
out=["total %d" % len(ps)]
for i in range(58,68):
    out.append("%d: %s" % (i+1, ps[i][:160]))
io.open(r"AI語譯/_work/review/_re0/nb02d.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
