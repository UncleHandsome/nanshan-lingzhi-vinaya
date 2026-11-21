# 對話材料 #0198

- event: assistant/message
- seq: 57301
- time: 1794606864463

---

{"command": "$env:PYTHONIOENCODING='utf-8'\n$py='C:\\Users\\lionc\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe'\n& $py -X utf8 -c @\"\nimport io,re\np=r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部\\_src\\mk_review_materials.py'\nt=io.open(p,encoding='utf-8').read()\n# 1) emit 清掉現譯可能自帶的【疏文】/【記文】/【鈔文】標籤\nt=t.replace(\\\"    L += ['■ %s（現譯）' % unit, '']\\n    for k in range(s0, s1):\\n        L += [o[k], '']\\\",\n            \\\"    L += ['■ %s（現譯）' % unit, '']\\n    for k in range(s0, s1):\\n        L += [re.sub(r'^【(?:疏文|記文|鈔文)】\\\\\\\\s*', '', o[k]), '']\\\")\nt=t.replace(\\\"        L += ['■ 記文（現譯）', '']\\n        for k in range(g0, g1):\\n            L += [o[k], '']\\\",\n            \\\"        L += ['■ 記文（現譯）', '']\\n        for k in range(g0, g1):\\n            L += [re.sub(r'^【(?:疏文|記文|鈔文)】\\\\\\\\s*', '', o[k]), '']\\\")\n# 2) 尼鈔提示詞再刪一句記文相關\nt=t.replace(\\\"    t = t.replace('；【記文】釋字或引詞在【疏文】是否留有銜接字眼', '')\\\",\n            \\\"    t = t.replace('；【記文】釋字或引詞在【疏文】是否留有銜接字眼', '')\\n    t = t.replace('或「銜接記文釋字須附原字」', '')\\\")\nio.open(p,'w',encoding='utf-8').write(t)\nimport ast; ast.parse(t); print('已套用 emit 清洗與尼鈔殘句移除，語法 OK')\n\"@", "description": "Apply material generator cleanups", "timeoutMs": 180000}