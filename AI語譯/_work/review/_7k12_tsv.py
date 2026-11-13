# -*- coding: utf-8 -*-
import io, sys, collections
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
import _7k12_edits

segs = collections.defaultdict(set)
for e in _7k12_edits.EDITS:
    segs[int(e["label"].split("-")[0])].add(e["label"])

doubt = {400: 1, 423: 1, 426: 1}
reject = {398: 1, 403: 2, 404: 2, 406: 3, 407: 2, 408: 1, 409: 1, 414: 1,
          417: 1, 418: 1, 420: 1, 421: 1, 423: 1, 429: 1, 430: 1, 433: 1}

p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r7k_done\01_行事鈔_卷下之四.tsv"
lines = ["檔號\t卷\t改段數\t否決\t存疑"]
for f in range(397, 435):
    lines.append("%d\t卷下之四\t%d\t%d\t%d" % (f, len(segs[f]), reject.get(f, 0), doubt.get(f, 0)))
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("\n".join(lines))
