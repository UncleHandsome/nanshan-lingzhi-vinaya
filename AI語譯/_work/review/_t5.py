import io
p=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out\02_戒疏\11a_卷三上之二.txt"
raw=io.open(p,encoding="utf-8",newline="").read()
lines=raw.split("\n")
print("eol_crlf", "\r" in raw, "lines", len(lines))
blank=[i+1 for i,l in enumerate(lines) if not l.strip()]
print("blank", blank)
