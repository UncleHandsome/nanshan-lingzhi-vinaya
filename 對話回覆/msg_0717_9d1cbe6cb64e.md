# 對話材料 #0717

- event: assistant/message
- seq: 100317
- time: 1794924751484

---

Packed material shows `【輸出標籤】【鈔文】` for 資持記 — that's wrong! 資持記 unit should be `記文`, but source `_裁決` materials maybe labeled 鈔文 because `mk_judge` uses labels from source `_材料` which for 資持記 may be `鈔文`? This is exactly the user's concern: 資持記 packing labels.

Check `_裁決` material units label for 資持記. `mk_judge` builds from `_材料` units; `_材料` for 資持記 likely label 記文? But pack shows 鈔文. Maybe `BC.fmt_for(book, units)` or pack_judge uses `unit` from book_config (資持記 unit='記文'), yet `【輸出標籤】【鈔文】` suggests `out_format` has 鈔文.

Inspect one original `_裁決` material head for 資持記.