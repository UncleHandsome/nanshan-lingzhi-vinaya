# 對話材料 #1359

- event: assistant/message
- seq: 137685
- time: 1795252954620

---

{"file_path": "C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部\\mk_jieshu_gap2_batches.py", "content": "import io, os, re\nB = r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\nsrc = os.path.join(B, '重作材料_長段', '戒疏_缺口_02.md')\nt = io.open(src, encoding='utf-8').read()\nblocks = {}\nfor m in re.finditer(r'### (G\\d+)\\s*\\n(.*?)(?=\\n### G|\\Z)', t, re.S):\n    blocks[m.group(1)] = m.group(2).strip()\nkeys = ['G%03d' % i for i in range(91, 181) if i != 93]\nprint('body', len(keys), 'available', sum(1 for k in keys if k in blocks))\nOUT = os.path.join(B, '重作材料_長段', '戒疏_缺口批次')\nfor idx, part in enumerate([keys[:30], keys[30:60], keys[60:]], 1):\n    body = []\n    for k in part:\n        if k in blocks:\n            body.append('\\n### %s\\n\\n%s\\n' % (k, blocks[k]))\n    text = '''# 戒疏缺口正文第二批 %02d\n\n## 規格\n- 依原文拆出【序文】【疏文】【記文】【註文】【律文】\n- 補現代標點\n- 每段各自配白話\n- 不改字、不增刪\n- 卷題目錄不譯\n\n## 輸出\n第一行：\n\n# 戒疏_缺口正文2_%02d\n\n空一行後，逐條：\n\n## G091\n### 1\n【疏文】原文\n【疏文】白話\n### 2\n【記文】原文\n【記文】白話\n\n---\n\n%s\n''' % (idx, idx, ''.join(body))\n    fp = os.path.join(OUT, '戒疏_缺口正文2_%02d.md' % idx)\n    io.open(fp, 'w', encoding='utf-8').write(text)\n    print(fp, len(body), part[0], part[-1])\n"}