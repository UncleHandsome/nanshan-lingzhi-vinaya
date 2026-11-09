import io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
out=json.load(open("_g2out.json",encoding="utf-8"))
p=r"AI語譯\_work\review\fix_re8_g2.tsv"
with io.open(p,"w",encoding="utf-8",newline="") as f:
    for ch,seg,t in out:
        assert "\t" not in t and "\n" not in t and "\r" not in t, (ch,seg)
        f.write("04_比丘尼鈔\t%s\t%s\t%s\n" % (ch,seg,t))
print("wrote", p, len(out), "lines")
