# 對話材料 #0217

- event: assistant/message
- seq: 58692
- time: 1794611874476

---

{"command": "$env:PYTHONIOENCODING='utf-8'\n$py='C:\\Users\\lionc\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe'\n& $py -X utf8 -c @\"\nimport sys,os,io\nB=r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\nsys.path.insert(0,os.path.join(B,'_src'))\nimport mk_review_materials as M, qwen_local as Q\np=M.get_prompt(False); n=M.get_prompt(True)\nchecks=['格式精簡','核對無誤','刪減無據增譯之賓語','依該句語境辨別','所釋之《戒本》','律制評價與屬性詞','按：','直引上文單字','動賓／修飾搭配']\nprint('疏記版：')\nfor c in checks: print('  %-16s %s'%(c,'有' if c in p else '★無'))\nprint('尼鈔版含記文殘留：', '【記文】' in n)\nprint()\nprint('系統 1(b)：', '律制寬嚴' in Q.SYSTEM_PROMPT)\nsch=[t['function']['parameters']['properties'].get('query',{}).get('description','') for t in Q.LOCAL_SCHEMAS if t['function']['name']=='local_search']\nprint('local_search query 說明：', sch)\n\"@", "description": "Verify the prompt and schema changes", "timeoutMs": 300000}