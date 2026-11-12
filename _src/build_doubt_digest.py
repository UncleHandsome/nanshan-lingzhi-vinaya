# -*- coding: utf-8 -*-
"""把 r2/r3 存疑材料彙總成可送裁判的小份文件。"""
import io, os, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '存疑材料')
OUT = os.path.join(SRC, '彙總')
os.makedirs(OUT, exist_ok=True)

PROMPT = '''你是南山律典譯文的資深校勘者。下面每條有一個「疑點」，是前一位校閱者不確定、暫時擱下的問題。

請對每一條給出明確結論，不要含糊：

1. 讀原文與譯文，判斷疑點成立不成立。
2. 結論只有三種：
   - 是錯：指出錯在哪，並給整段替換文字。
   - 不是錯：說明為什麼原文支持現行譯法。
   - 材料不足：指出缺什麼（例如需要查某部論、某卷律），不要猜。

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
- 不要為了有結論而硬判；材料不足就寫材料不足。
- 不要改原文、不要合併段落、不要加譯者按語。
'''

# 抽出各檔的「條目塊」：以 ### 或 - ** 開頭，含段號
blocks = []
for f in glob.glob(os.path.join(SRC, 'r2_存疑', '*.md')) + glob.glob(os.path.join(SRC, 'r3_存疑', '*.md')):
    tag = os.path.basename(os.path.dirname(f)) + '/' + os.path.basename(f)
    text = io.open(f, encoding='utf-8').read()
    parts = re.split(r'\n(?=#{2,4}\s|\s*[-*]\s*\*\*\d)', text)
    for p in parts:
        p = p.strip()
        if not p or len(p) < 30:
            continue
        if re.search(r'\d{3}-\d{4}', p):
            blocks.append((tag, p))

print('抽出條目塊', len(blocks))

# 每 10 塊一份
size = 10
n = 0
for i in range(0, len(blocks), size):
    n += 1
    part = blocks[i:i + size]
    body = '\n\n---\n\n'.join('%s\n\n%s' % (tag, blk) for tag, blk in part)
    txt = '# 存疑裁判材料 %02d（%d 條）\n\n## 裁判提示詞（全文）\n\n```text\n%s```\n\n## 材料開始\n\n%s\n' % (n, len(part), PROMPT, body)
    io.open(os.path.join(OUT, '存疑_%02d.md' % n), 'w', encoding='utf-8').write(txt)

print('切成', n, '份')
