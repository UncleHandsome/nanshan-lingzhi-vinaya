import io, sys
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
import _z6_lib as L
lines=[]
for n in range(1744,1769):
    lines.append(L.show(n))
io.open(r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_z6_show_1744_1768.txt","w",encoding="utf-8",newline="\n").write("\n".join(lines))
print("ok")
