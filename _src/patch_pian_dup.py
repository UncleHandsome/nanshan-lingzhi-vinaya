import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

# 1) 片段先登記 used，避免同一記段又被整段輸出
s = s.replace("""        for part, tr, c in zip(parts, ts, tg):
            pieces.setdefault(c, []).append((n, part, tr))""",
"""        for part, tr, c in zip(parts, ts, tg):
            pieces.setdefault(c, []).append((n, part, tr))
            used.add(n)""")
s = s.replace("""    pieces = {}
    for e in splits:""", """    pieces = {}
    used = set()
    for e in splits:""")
# 移除後面重複宣告
s = s.replace("""    used = set()
    for cno, it in enumerate(chao, 1):""", """    for cno, it in enumerate(chao, 1):""")

# 2) 強化頁眉清理
s = s.replace("""HDR = re.compile(r'^(?:四分律行事鈔資持記[^ ]*\\s*)?(?:\\d+\\s*)?釋[\\u4e00-\\u9fff]{1,6}篇(?:\\([^)]*\\))?\\s*')""",
"""HDR = re.compile(r'(?:四分律行事鈔資持記[^ ]{0,12}\\s*)?(?:\\d+\\s*)?釋[\\u4e00-\\u9fff]{1,6}篇(?:\\([^)）]*\\))?\\s*')""")
s = s.replace("""def clean(t):
    return HDR.sub('', t)""",
"""def clean(t):
    head, rest = t[:80], t[80:]
    return HDR.sub('', head) + rest""")
io.open(p, 'w', encoding='utf-8').write(s)
print('dup + header fixed')
