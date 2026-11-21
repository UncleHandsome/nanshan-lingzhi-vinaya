# 對話材料 #0022

- event: assistant/message
- seq: 1173
- time: 1793882424862

---

{"file_path": "_src/apply_labels.py", "new_string": "        out = []\n        for i, seg in enumerate(ps):\n            body = seg.strip()\n            while True:                      # 去掉重覆的舊標籤（如【疏文】【疏】…）\n                nb = LEAD.sub('', body).strip()\n                if nb == body:\n                    break\n                body = nb\n            L = lay[i]", "old_string": "        out = []\n        for i, seg in enumerate(ps):\n            body = LEAD.sub('', seg).strip()\n            L = lay[i]"}