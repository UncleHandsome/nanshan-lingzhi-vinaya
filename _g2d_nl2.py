import json
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
for i in (50,54,51):
    c=rows[i]["current"]; k=c.find("\n")
    print("ROW",i,"pos",k,"len",len(c))
    print("  before:",repr(c[max(0,k-40):k]))
    print("  after :",repr(c[k:k+40]))
c=rows[51]["current"]
print("row51 first 5 newline contexts:")
start=0
for _ in range(5):
    k=c.find("\n",start)
    print("   ",repr(c[max(0,k-15):k]),"|",repr(c[k:k+15]))
    start=k+1
print("row51 newline count", c.count("\n"))
