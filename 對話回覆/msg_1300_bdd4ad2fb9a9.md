# 對話材料 #1300

- event: assistant/message
- seq: 136464
- time: 1795251551863

---

R001:
- pairs 2-7 `【疏文】` should `【序文】`.
- pair 7 has background residue; pair 3 maybe truncated source? Pair 3 printed source ends `【` maybe has background.
- pair 10 has prompt residue in translation.
Need apply:
- For pairs 2-7, change `【疏文】` to `【序文】`.
- Remove `【後文背景（節錄）】...` and `【分段要求】...` from source/tr for all first 10.
- Pair 3 source maybe missing end? R001 corrected text has full; current source truncated at `【` due background? Need compare lengths; not fix content now.

Implement script first 8 pairs:
- Replace prefix label.
- Split source/tr at `【後文背景`/`【分段要求`.
- Preserve HTML.

Then R008/R009 labels: find pairs in 卷二 whose source starts `次科，「通約山水」` and `初明廢中`; change label to `【記文】`.
Do.

Also pair 10 R? prompt residue; clear.

Write script.