import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

# 還原全域替換
s = s.replace("if i2 >= body_start and toc_match(bk['out'], o):", "if toc_match(bk['out'], o):")

# 移除舊 body_start 區塊
start = s.find("            # 義鈔／尼鈔：卷首目次不列入篇目")
if start > 0:
    end = s.find("            # 偵測「連續篇名」的卷首目次", start)
    s = s[:start] + s[end:]

# 只改頁面建置那段（用 it['o'] 那次）
old = """                if toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)"""
new = """                if (bk['out'] not in ('yichao', 'nicao') or i2 >= body_start) and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)"""
if old in s:
    s = s.replace(old, new, 1)

# 在頁面迴圈開頭定義 body_start
old2 = """            toc = []
            # 偵測「連續篇名」的卷首目次，整段略過（側欄已有篇目）"""
new2 = """            toc = []
            body_start = 0
            if bk['out'] in ('yichao', 'nicao'):
                for i2, it2 in enumerate(items):
                    if '【' in it2['o']:
                        body_start = i2
                        break
            # 偵測「連續篇名」的卷首目次，整段略過（側欄已有篇目）"""
if old2 in s and 'body_start = 0' not in s:
    s = s.replace(old2, new2, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('patched cleanly')
