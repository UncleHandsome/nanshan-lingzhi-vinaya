# -*- coding: utf-8 -*-
import io
p=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\說明_r2_02d.md"
t=io.open(p,encoding="utf-8").read()
t=t.replace("**294 處／224 段**","**295 處／224 段**")
t=t.replace("| **791 條** |","| **790 條** |")
t=t.replace("| 10c_卷三上之一 | 108 | 20 | 22 |","| 10c_卷三上之一 | 108 | 20 | 23 |")
t=t.replace("| **1,130** | **224** | **294** |","| **1,130** | **224** | **295** |")
t=t.replace("## 六、否決分類（791 條，約數）","## 六、否決分類（790 條，約數）")
t=t.replace("| 只是潤飾／精度偏好（改法可，但不屬譯錯） | 402 |","| 只是潤飾／精度偏好（改法可，但不屬譯錯） | 401 |")
t=t.replace("294 處替換逐筆檢查唯一性","295 處替換逐筆檢查唯一性")
io.open(p,"w",encoding="utf-8",newline="").write(t)
print("ok")
