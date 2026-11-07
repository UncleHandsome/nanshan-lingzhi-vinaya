import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

# 移除壞掉的 body_start 條件
s = s.replace("if (bk['out'] not in ('yichao', 'nicao') or i2 >= body_start) and toc_match(bk['out'], o):",
              "if i2 not in drop_toc and toc_match(bk['out'], o):")

# 移除殘留的 body_start 區塊
start = s.find("            body_start = 0")
if start > 0:
    end = s.find("            # 偵測「連續篇名」的卷首目次", start)
    s = s[:start] + s[end:]

# 在 toc=[] 後加入 drop_toc 計算
old = """            toc = []
            # 偵測「連續篇名」的卷首目次，整段略過（側欄已有篇目）"""
new = """            toc = []
            # 卷首目次：開頭連續 3 個以上的短篇名，不列入篇目（仍照常顯示）
            drop_toc = set()
            run3 = []
            for i2, it2 in enumerate(items[:40]):
                o2 = it2['o'].strip()
                if toc_match(bk['out'], o2) and len(re.sub(r'[^\\u4e00-\\u9fff]', '', o2)) <= 10:
                    run3.append(i2)
                else:
                    if len(run3) >= 3:
                        drop_toc.update(run3)
                    run3 = []
            if len(run3) >= 3:
                drop_toc.update(run3)
            # 偵測「連續篇名」的卷首目次，整段略過（側欄已有篇目）"""
if old in s and 'drop_toc' not in s:
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('drop_toc patched')
