# -*- coding: utf-8 -*-
"""產出 172-206 每段的「材料譯文 vs 現行 out」差異摘要（緊湊格式）。"""
import os, sys, json, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _7kv_lib as L

IDS = list(range(172, 207))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_7kv_diff.md")
lines = []
for n in IDS:
    items = L.parse_material(n)
    lines.append("\n## %d（%d 段）" % (n, len(items)))
    cache = {}
    for it in items:
        ch = it["chunk"]
        if ch not in cache:
            cache[ch] = L.chunk_paras(ch)[3]
        pm = cache[ch]
        cur = pm[it["seg"] - 1][1]
        old = it["tr"]
        if cur == old:
            lines.append("- %s  #%d 相同" % (it["label"], it["seg"]))
            continue
        sm = difflib.SequenceMatcher(None, old, cur, autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
        lines.append("- %s  #%d  len old=%d cur=%d  差異 %d 處" % (it["label"], it["seg"], len(old), len(cur), len(ops)))
        for tag, i1, i2, j1, j2 in ops[:40]:
            pre = old[max(0, i1 - 12):i1].replace("\n", " ")
            post = old[i2:i2 + 12].replace("\n", " ")
            lines.append("    [%s] …%s〔%s〕→〔%s〕%s…" % (tag, pre, old[i1:i2], cur[j1:j2], post))
        if len(ops) > 40:
            lines.append("    …其餘 %d 處略" % (len(ops) - 40))

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("wrote", OUT, "lines", len(lines))
