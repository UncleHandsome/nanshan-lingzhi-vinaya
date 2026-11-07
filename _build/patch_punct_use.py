import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
s = io.open(p, encoding='utf-8').read()

old = """def pairs_global(src_dir, tr_tag, ju_file):
    \"\"\"尼鈔、義鈔：整本 句讀_clean.txt。\"\"\"
    ju = [x.strip() for x in re.split(r'\\n\\s*\\n', io.open(ju_file, encoding='utf-8').read()) if x.strip()]
    src_all, tr_all, keys = [], [], []
    for key, sp, tt in load_chunks(src_dir, tr_tag):
        for i in range(min(len(sp), len(tt))):
            src_all.append(sp[i])
            tr_all.append(tt[i])
            keys.append(key)
    buckets, _ = assign(ju, src_all)
    res = []
    cur_vol = None
    entries = []
    for i, key in enumerate(keys):
        o = '　'.join(buckets[i]) if buckets[i] else src_all[i]"""
new = """PUNCT_MAPS = {'04_比丘尼鈔': 'nicao_punct.json', '05_拾毗尼義鈔': 'yichao_punct.json'}


def pairs_global(src_dir, tr_tag, ju_file):
    \"\"\"尼鈔、義鈔：整本 句讀_clean.txt（優先使用字元錨點取回的帶標點段落）。\"\"\"
    ju = [x.strip() for x in re.split(r'\\n\\s*\\n', io.open(ju_file, encoding='utf-8').read()) if x.strip()]
    src_all, tr_all, keys = [], [], []
    for key, sp, tt in load_chunks(src_dir, tr_tag):
        for i in range(min(len(sp), len(tt))):
            src_all.append(sp[i])
            tr_all.append(tt[i])
            keys.append(key)
    punct = None
    pm = PUNCT_MAPS.get(src_dir)
    if pm:
        pth = os.path.join(B, 'AI語譯', '_work', pm)
        if os.path.exists(pth):
            punct = json.load(io.open(pth, encoding='utf-8'))
    buckets, _ = assign(ju, src_all)
    res = []
    cur_vol = None
    entries = []
    for i, key in enumerate(keys):
        o = '　'.join(buckets[i]) if buckets[i] else src_all[i]
        if punct and i < len(punct) and re.search(r'[，。、；：？！」]', punct[i]):
            o = punct[i]"""
if old in s and 'PUNCT_MAPS' not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('pairs_global uses punct maps')
else:
    print('already patched or missing')
