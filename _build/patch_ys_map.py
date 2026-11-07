import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("""    punct = None
    pth = os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json')
    if os.path.exists(pth):
        punct = json.load(io.open(pth, encoding='utf-8'))""",
"""    punct = None
    pth = os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json')
    if os.path.exists(pth):
        punct = json.load(io.open(pth, encoding='utf-8'))
    amap = None
    pth2 = os.path.join(B, 'AI語譯', '_work', 'ys_align_map.json')
    if os.path.exists(pth2):
        amap = json.load(io.open(pth2, encoding='utf-8'))""")

s = s.replace("""        n = min(len(sp), len(tt))
        for i in range(n):
            gi += 1
            o = sp[i]
            if punct and gi < len(punct) and re.search(r'[，。、；：？！]', punct[gi]):
                o = punct[gi]
            entries.append((o, tt[i]))""",
"""        n = min(len(sp), len(tt))
        mp = amap.get(key) if amap else None
        for i in range(n):
            gi += 1
            o = sp[i]
            if punct and gi < len(punct) and re.search(r'[，。、；：？！]', punct[gi]):
                o = punct[gi]
            j = i
            if mp and i < len(mp) and 0 <= mp[i] < len(tt):
                j = mp[i]
            entries.append((o, tt[j]))""")
io.open(p, 'w', encoding='utf-8').write(s)
print('pairs_simple uses ys_align_map')
