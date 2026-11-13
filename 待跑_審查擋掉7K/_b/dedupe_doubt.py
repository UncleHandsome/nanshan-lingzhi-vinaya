# -*- coding: utf-8 -*-
"""去重：把第三方補寫且 chunk 歸屬有誤的重複節，改為「指路」註記（不刪他人檔案其他內容）。"""
import io, os

P = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\存疑材料\7K_存疑.md"
raw = io.open(P, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw else "\n"
n = raw.replace("\r\n", "\n")

start = n.find("## 02_戒疏（後 12 檔：695–1256）")
end = n.find("## 02_戒疏（後12：695–1256，2026-11-12 13:14 補回）")
assert start > 0 and end > start, (start, end)

NOTE = """## 02_戒疏（後 12 檔：695–1256）

> 本節原有另一支據 `處理記錄.tsv` 補寫的兩條（841-0003、1098-0008），其 chunk 歸屬有誤：
> 841-0003 在 `09d_卷二下之二#126`（非 08a 行事鈔）、1098-0008 在 `16c_卷四上之一#83`（非 14a 卷三之三）。
> 原工作已於本檔末尾補回完整條目，見下方「02_戒疏（後12：695–1256，2026-11-12 13:14 補回）」；
> 為免同檔重複兩份，本節僅留指路。

---

"""

n2 = n[:start] + NOTE + n[end:]
out = n2.replace("\n", eol) if eol == "\r\n" else n2
io.open(P, "w", encoding="utf-8", newline="").write(out)
print("rewrote, size=%d" % os.path.getsize(P))
