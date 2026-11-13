import io, os, re
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
p = os.path.join(base, "校閱_7K", "校閱_207.txt")
t = io.open(p, encoding="utf-8", newline="").read()
print("len", len(t), "has CRLF", "\r\n" in t)
t2 = t.replace("\r\n", "\n")
lines = t2.split("\n")
for i, line in enumerate(lines[:12], 1):
    print(i, ascii(line[:60]))
pat = re.compile(r"^【(\d{4}-\d{4})】(\S+)#(\d+)$", re.M)
print("matches", [ascii(m) for m in pat.findall(t2)])
