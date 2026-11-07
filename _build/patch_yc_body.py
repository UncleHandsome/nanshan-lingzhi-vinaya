import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

# 1) 撤掉剛才的短篇名 run-drop
start = s.find("            # 連續短篇名（卷首目次）整段略過")
end = s.find("            for i2, it in enumerate(items):", start)
if start > 0 and end > start:
    s = s[:start] + s[end:]

# 2) 只對「卷首之後」的段落做篇目判定（義鈔／尼鈔）
old = """            toc = []
            # 偵測「連續篇名」的卷首目次，整段略過（側欄已有篇目）"""
new = """            toc = []
            # 義鈔／尼鈔：卷首目次不列入篇目
            body_start = 0
            if bk['out'] in ('yichao', 'nicao'):
                for i2, it2 in enumerate(items):
                    if '卷上之一' in it2['o'] or '卷上' == v:
                        if '【' in it2['o'] and '卷' in it2['o']:
                            body_start = i2
                            break
            # 偵測「連續篇名」的卷首目次，整段略過（側欄已有篇目）"""
if old in s and 'body_start' not in s:
    s = s.replace(old, new, 1)

# 3) toc 判定加 body_start 條件
s = s.replace("if toc_match(bk['out'], o):", "if i2 >= body_start and toc_match(bk['out'], o):")
io.open(p, 'w', encoding='utf-8').write(s)
print('site2 rollback + body_start patched')
