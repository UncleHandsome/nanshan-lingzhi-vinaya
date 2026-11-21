# 對話材料 #0362

- event: assistant/message
- seq: 70950
- time: 1794749504789

---

The label newline didn't apply (still '【鈔文】第四' no newline). The regex insertion likely failed due to escaping ($). Let me check norm.py content and fix with edit tool instead.

Also need to handle: label newline should be inserted after label only if text follows on same line; for existing newline keep.

Let me read norm.py normalize section.