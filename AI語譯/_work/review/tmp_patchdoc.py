# -*- coding: utf-8 -*-
import io
p="說明_r2_02b.md"; s=io.open(p,encoding="utf-8").read()
old="- 其餘各檔以「嚴重度前 5 條逐條核 + 其餘區塊摘要掃過」處理；每 chunk 平均深核 5 條、掃過 40–70 條。此為本輪方法上限，非全量逐條。"
new=old+"\n- 未深核的其餘意見（共 1,356 條，含 id／段號／分數／首 110 字）已整理為 `_r2_02/_r2b_leftover.txt`，可直接續跑，不必重跑定位。"
assert old in s
s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("patched",len(s))
