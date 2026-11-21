# 對話材料 #0145

- event: assistant/message
- seq: 54804
- time: 1794563969674

---

{"command": "$env:PYTHONIOENCODING='utf-8'\n$py='C:\\Users\\lionc\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe'\n& $py -X utf8 -c @\"\nimport io,os,glob\nB=r'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\nNEW='''你是南山律典審校編輯，負責核對《四分律》與南山三大部／三大記的白話譯文是否忠實準確。\n\n請**只審查【本次待審段】**，前後背景僅供確認主詞、指代與因果，不需校對。\n\n### 請依序輸出以下三欄：\n\n1. **逐句對位與脈絡確認**：\n   - 把本段原文按句切開，**逐句**將最小語義單位對照現譯（特別確認：否定詞、因果／選擇連詞、引號內是否偷加字、文言字詞是否未翻完）。\n   - 結合前後背景，確認主詞、受詞、「此戒／彼／其」等指代在現譯中是否正確。\n   - 專有名詞、人名、戒律典故若無法 100% 確定，須標註。\n   - **段內每一句都要對位，不可只對完第一句就跳過其餘。**\n\n2. **錯誤檢查（嚴禁吹毛求疵）**：\n   - 只抓實質問題：漏譯、增譯（含擅造校勘註或引號改字）、誤譯、文言殘留未譯、術語／人名錯、主客或因果顛倒、句法讀不通。\n   - 禁止挑純修辭問題。\n   - **整段每個詞都掃描過，不可找到一個錯就停。**\n\n3. **修正後的譯文（完整輸出，可直接取代現譯）**：\n   - 格式固定為兩行：\n     【疏文】……\n     【記文】……\n   - 給**完整譯文**，不是只給改動處；未需修改的部分照原譯抄回。\n   - **不要**加「（未改）」「（原文如此）」「※修正」這類標記，也不要夾註說明。\n   - 譯文用自然流暢的現代中文，段落不換行。'''\nd=os.path.join(B,'測試','業疏_疏記20組')\nn=0\nfor p in sorted(glob.glob(os.path.join(d,'*.md'))):\n    t=io.open(p,encoding='utf-8').read()\n    i=t.find('\\n---\\n')\n    io.open(p,'w',encoding='utf-8').write(NEW+'\\n'+(t[i:] if i>0 else t))\n    n+=1\nprint('已更新提示詞：%d 份'%n)\n\"@\n\"=== 預覽 ===\"\nGet-Content 'C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部\\測試\\業疏_疏記20組\\01.md' -Encoding UTF8 | Select-Object -First 34", "description": "Update prompt to output corrected translation directly", "timeoutMs": 300000}