import json
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
out=[]
c=rows[51]["current"]
for needle in ["比丘尼對出家男","離五衣","三重二輕","二輕","同坐"]:
    k=c.find(needle)
    out.append("needle=%r pos=%d count=%d" % (needle,k,c.count(needle)))
k=c.find("比丘尼對出家男")
if k>=0:
    out.append("CONTEXT:\n..."+c[max(0,k-700):k+700]+"...")
out.append("\n===== ROW84 FULL =====")
out.append(rows[84]["current"])
out.append("\n===== ROW51 len=%d ROW52 same=%s" % (len(rows[51]["current"]), rows[51]["current"]==rows[52]["current"]))
open("_g2d_ctx2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
