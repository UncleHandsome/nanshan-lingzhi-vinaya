# -*- coding: utf-8 -*-
"""存疑彙總：以「一本書一個檔」為單位，保留原檔結構，只前置裁判提示詞。"""
import io, os, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '存疑材料')
OUT = os.path.join(SRC, '彙總')

PROMPT = '''你是南山律典譯文的資深校勘者。下面每條有一個「疑點」，是前一位校閱者不確定、暫時擱下的問題。

請對每一條給出明確結論，不要含糊：
1. 讀原文與譯文，判斷疑點成立不成立。
2. 結論只有三種：
   - 是錯：指出錯在哪，並給整段替換文字。
   - 不是錯：說明為什麼原文支持現行譯法。
   - 材料不足：指出缺什麼，不要猜。

輸出格式（每條一段）：
### <段號>｜是錯
判斷：…
建議：（整段替換文字，其餘與現譯逐字相同）

### <段號>｜不是錯
判斷：…

### <段號>｜材料不足
判斷：需查…，現有材料無法判定。

規則：
- 「是錯」才給建議，且必須是完整段落。
- 不要硬判；材料不足就寫材料不足。
- 不要改原文、不要合併段落、不要加譯者按語。
'''

os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, '*.md')):
    os.remove(f)

files = sorted(glob.glob(os.path.join(SRC, 'r2_存疑', '*.md'))) + \
        sorted(glob.glob(os.path.join(SRC, 'r3_存疑', '*.md')))
for f in files:
    batch = os.path.basename(os.path.dirname(f)).replace('_存疑', '')
    book = os.path.splitext(os.path.basename(f))[0]
    body = io.open(f, encoding='utf-8').read().strip()
    txt = ('# 存疑裁判材料：%s（%s 批）\n\n## 裁判提示詞（全文）\n\n```text\n%s```\n\n## 材料開始\n\n%s\n'
           % (book, batch, PROMPT, body))
    name = '存疑_%s_%s.md' % (batch, book.replace('其他三書', '其他'))
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(txt)
    print('%-32s %5.1f KB' % (name, len(txt.encode('utf-8')) / 1024))
