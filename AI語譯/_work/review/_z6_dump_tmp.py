import io, os, sys
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
import _z6_lib as L
nums = list(range(1744, 1769))
out = []
for n in nums:
    segs = L.mat(n)
    out.append("##### %d : %d segs #####" % (n, len(segs)))
    for s in segs:
        out.append("=== %s %s#%d ===" % (s["idx"], s["chunk"], s["para"]))
        out.append("[原] " + s["orig"])
        out.append("[現] " + L.para(s["chunk"], s["para"]))
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_z6_dump_1744_1768.txt"
with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out))
print("wrote", p, len(out))
