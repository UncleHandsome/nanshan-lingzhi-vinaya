import json, sys
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
def show(i, needle, before=300, after=300):
    c = rows[i]["current"]
    out=["=== ROW %d gid=%s len=%d needle=%r" % (i, rows[i]["gid"], len(c), needle)]
    k = c.find(needle)
    if k < 0:
        out.append("  NOT FOUND")
    else:
        n = c.count(needle)
        out.append("  occurrences=%d pos=%d" % (n,k))
        out.append("  ..."+c[max(0,k-before):k+len(needle)+after]+"...")
    return "\n".join(out)
res=[]
res.append(show(48,"難道不犯逆罪嗎",250,250))
res.append(show(49,"佛陀卻開許他受具足戒",250,250))
res.append(show(50,"殺化人的得偷蘭遮",200,300))
res.append(show(83,"摩訶僧祇律論",200,200))
open("_g2d_ctx1.txt","w",encoding="utf-8").write("\n\n".join(res))
print("ok")
