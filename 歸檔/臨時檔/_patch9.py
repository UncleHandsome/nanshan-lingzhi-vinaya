import io
p = r"AI語譯/_work/review/_re0_export.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('md.append("  - **套用修訂：186 條**，合併為 **177 段**（同段多條已合併）。")',
 'md.append("  - **套用修訂：%d 條**，合併為 **%d 段**（同段多條已合併）。" % (len(json.load(io.open(os.path.join(OUT, "applied.json"), encoding="utf-8"))), len(rows)))')
s = s.replace('md.append("  - **錯位：4 條**（建議所改文字實屬他段，未套用，另列 `re0_錯位.tsv`）。")',
 'md.append("  - **錯位：%d 條**（建議所改文字實屬他段，未套用，另列 `re0_錯位.tsv`）。" % len(mis))')
s = s.replace('md.append("| 錯位 | — | — | 4 |")', 'md.append("| 錯位 | — | — | %d |" % len(mis))')
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
