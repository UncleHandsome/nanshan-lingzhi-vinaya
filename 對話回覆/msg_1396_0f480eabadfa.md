# 對話材料 #1396

- event: assistant/message
- seq: 139140
- time: 1795255293299

---

{"file_path": "C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部\\mk_nicao4.py", "content": "import io, os, re\nB = r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\nsrc = os.path.join(B, '重作材料_長段', '尼鈔_14缺口_最新.md')\nt = io.open(src, encoding='utf-8').read()\nblocks = {m.group(1): m.group(2).strip() for m in re.finditer(r'^## (H\\d+)\\s*\\n(.*?)(?=\\n## H|\\Z)', t, re.M | re.S)}\nkeys = ['H003', 'H012', 'H013', 'H014']\nbody = []\nfor k in keys:\n    body.append('\\n## %s\\n\\n%s\\n' % (k, blocks.get(k, '（缺）')))\ntext = '''# 尼鈔 4 個真正缺譯缺口\n\n這 4 條在 `_終審`／`_終修` 沒有現成譯文，需補譯。\n\n## 規格\n- 依原文補現代標點\n- 只譯正文，不改字、不增刪\n- 每條輸出：\n  - H003\n  - 【鈔文】原文\n  - 【鈔文】白話\n\n## 輸出\n第一行：\n\n# 尼鈔_4真缺口\n\n空一行後，逐條。\n\n---\n\n%s\n''' % ''.join(body)\nfp = os.path.join(B, '重作材料_長段', '尼鈔_4真缺口.md')\nio.open(fp, 'w', encoding='utf-8').write(text)\nprint(fp, len(keys))\n"}