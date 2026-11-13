# -*- coding: utf-8 -*-
import io
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\存疑材料\7K_存疑.md"
add = u"""

## 資持記 上一上（7K，檔 1294–1303）

1. **1297-0001「依根附教」**：原譯「依據根機依附教法」。審閱意見另讀為「依所犯的根本（情節輕重）、附合教文」，與上句「據刑」為對文。鈔文只作「依根附教，各有差降」，記文於此無別釋，兩讀皆通；現譯取「根機」義未改，存疑待後定。
"""
with io.open(p, "a", encoding="utf-8", newline="") as f:
    f.write(add)
print("appended")
