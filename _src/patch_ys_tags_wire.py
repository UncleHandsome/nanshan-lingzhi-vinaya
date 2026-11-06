import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("""    amap = None
    pth2 = os.path.join(B, 'AI語譯', '_work', 'ys_align_map.json')""",
"""    ytags = None
    pth3 = os.path.join(B, 'AI語譯', '_work', 'yeshu_tags.json')
    if os.path.exists(pth3):
        ytags = json.load(io.open(pth3, encoding='utf-8'))
    amap = None
    pth2 = os.path.join(B, 'AI語譯', '_work', 'ys_align_map.json')""")

s = s.replace("""            if punct and gi < len(punct) and re.search(r'[，。、；：？！]', punct[gi]):
                o = punct[gi]
                mtag = re.match(r'^【[律疏記註]】', sp[i].strip())
                if mtag and '【' not in o[:4]:
                    o = mtag.group(0) + o""",
"""            if punct and gi < len(punct) and re.search(r'[，。、；：？！]', punct[gi]):
                o = punct[gi]
            if ytags and 0 <= gi < len(ytags) and ytags[gi] and not o.startswith('【'):
                o = ytags[gi] + o""")
io.open(p, 'w', encoding='utf-8').write(s)
print('tags wired')
