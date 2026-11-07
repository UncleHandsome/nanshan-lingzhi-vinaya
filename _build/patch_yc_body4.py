import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

# 1) 預先計算那段：加 drop_toc
s = s.replace("""            for i2, it in enumerate(items):
                if i2 in drop:
                    continue
                o = it['o'].strip()
                if re.match(r'^\\d+\\s*[\\u4e00-\\u9fff]{2,10}篇\\(上[一二三四五六七八九十]?\\)$', o):
                    continue
                if i2 not in drop_toc and toc_match(bk['out'], o):""",
"""            drop_toc = set()
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
            for i2, it in enumerate(items):
                if i2 in drop:
                    continue
                o = it['o'].strip()
                if re.match(r'^\\d+\\s*[\\u4e00-\\u9fff]{2,10}篇\\(上[一二三四五六七八九十]?\\)$', o):
                    continue
                if i2 not in drop_toc and toc_match(bk['out'], o):""")

# 2) 頁面建置那段：同樣加 drop_toc 並套用
s = s.replace("""            for i2, it in enumerate(items):
                if i2 in drop:
                    continue
                o = it['o'].strip()
                # 略過卷首「1 X篇(上一)」這種重複的目次序號行""",
"""            drop_toc = set()
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
            for i2, it in enumerate(items):
                if i2 in drop:
                    continue
                o = it['o'].strip()
                # 略過卷首「1 X篇(上一)」這種重複的目次序號行""")

s = s.replace("""                if toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)""",
"""                if i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)""")
io.open(p, 'w', encoding='utf-8').write(s)
print('drop_toc applied to both loops')
