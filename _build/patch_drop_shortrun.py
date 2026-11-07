import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

old = """            for i2, it in enumerate(items):
                if i2 in drop:
                    continue"""
new = """            # 連續短篇名（卷首目次）整段略過
            run2 = []
            for i2, it2 in enumerate(items):
                o2 = it2['o'].strip()
                if toc_match(bk['out'], o2) and len(re.sub(r'[^\\u4e00-\\u9fff]', '', o2)) <= 10:
                    run2.append(i2)
                else:
                    if len(run2) >= 3:
                        drop.update(run2)
                    run2 = []
            if len(run2) >= 3:
                drop.update(run2)
            for i2, it in enumerate(items):
                if i2 in drop:
                    continue"""
if old in s and '連續短篇名' not in s:
    s = s.replace(old, new, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('run-drop for short toc lines added')
else:
    print('block missing or patched')
