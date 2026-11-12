# -*- coding: utf-8 -*-
"""依「書」分組彙總存疑材料（不機械切，保證每條完整）。"""
import io, os, re, glob, collections

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

# 收集：以「###」或「- **」等標題開頭的完整條目
items = []  # (書, 段號, 全文)
for f in sorted(glob.glob(os.path.join(SRC, 'r2_存疑', '*.md')) + glob.glob(os.path.join(SRC, 'r3_存疑', '*.md'))):
    book_hint = os.path.splitext(os.path.basename(f))[0]
    text = io.open(f, encoding='utf-8').read()
    # 以 markdown 標題或編號項目為界
    parts = re.split(r'\n(?=#{3,4}\s|\s*[-*]\s+\*\*)', text)
    for p in parts:
        p = p.strip()
        if len(p) < 40:
            continue
        m = re.search(r'(\d{3})-\d{4}', p)
        if not m:
            continue
        book = book_hint if book_hint not in ('其他三書',) else '其他三書'
        # 若條目內文有 book/chunk 標記，採用之
        mb = re.search(r'(0[1-5]_[^\s/｜|#，。\n]{1,12}|資持記)', p)
        if mb and mb.group(1) not in ('其他三書',):
            book = mb.group(1)
        items.append((book, p))

print('收集條目', len(items))
bybook = collections.defaultdict(list)
for b, p in items:
    bybook[b].append(p)

for f in glob.glob(os.path.join(OUT, '*.md')):
    os.remove(f)
os.makedirs(OUT, exist_ok=True)

LIMIT = 22000  # 每份上限 22 KB
for book, ps in sorted(bybook.items()):
    # 依序堆疊，超過上限就換一份（在條目邊界）
    chunks, cur, cur_sz = [], [], 0
    for p in ps:
        sz = len(p.encode('utf-8'))
        if cur and cur_sz + sz > LIMIT:
            chunks.append(cur); cur, cur_sz = [], 0
        cur.append(p); cur_sz += sz
    if cur:
        chunks.append(cur)
    for i, ch in enumerate(chunks, 1):
        suffix = '' if len(chunks) == 1 else '_%d' % i
        name = '存疑_%s%s.md' % (book.replace('_', ''), suffix)
        body = '\n\n---\n\n'.join(ch)
        txt = ('# 存疑裁判材料：%s（%d 條）\n\n## 裁判提示詞（全文）\n\n```text\n%s```\n\n## 材料開始\n\n%s\n'
               % (book, len(ch), PROMPT, body))
        io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(txt)
        print('%-28s %2d 條 %5.1f KB' % (name, len(ch), len(txt.encode('utf-8')) / 1024))
