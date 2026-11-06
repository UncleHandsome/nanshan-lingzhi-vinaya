import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site2.py'
s = io.open(p, encoding='utf-8').read()

KNOWN = ("{'集法緣成篇第一','諸界結解篇第二','諸戒受法篇第三','衣藥受淨篇第四',"
         "'諸說戒法篇第五','諸眾安居法篇第六','諸眾自恣法篇第七','諸分衣法篇第八',"
         "'懺六聚法篇第九','雜法住持篇第十'}")

# 預先計算迴圈
s = s.replace("""                    if bk['out'] == 'jieshu' and v in ('卷一', '卷一上') and _lb not in ('序文', '凡例', '目錄', '條目'):
                        _lb = ''
                    if _lb and _lb not in [n for _, n in tt]:""",
"""                    if bk['out'] == 'jieshu' and v in ('卷一', '卷一上') and _lb not in ('序文', '凡例', '目錄', '條目'):
                        _lb = ''
                    if bk['out'] == 'yeshu' and _lb not in """ + KNOWN + """:
                        _lb = ''
                    if _lb and _lb not in [n for _, n in tt]:""")

# 頁面建置迴圈
s = s.replace("""                    if bk['out'] == 'jieshu' and v in ('卷一', '卷一上') and _lb not in ('序文', '凡例', '目錄', '條目'):
                        _lb = ''
                    if _lb and _lb not in [n for _, n in toc]:""",
"""                    if bk['out'] == 'jieshu' and v in ('卷一', '卷一上') and _lb not in ('序文', '凡例', '目錄', '條目'):
                        _lb = ''
                    if bk['out'] == 'yeshu' and _lb not in """ + KNOWN + """:
                        _lb = ''
                    if _lb and _lb not in [n for _, n in toc]:""")
io.open(p, 'w', encoding='utf-8').write(s)
print('yeshu whitelist added')
