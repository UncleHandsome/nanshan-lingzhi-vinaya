import json, os

rows = json.load(open(r'AI語譯\_work\review\tmp_g3_rows.json', encoding='utf-8'))
idx = [3, 10, 21, 26, 28, 29, 35, 39, 40]
outdir = r'AI語譯\_work\review\tmp_g3_cur'
os.makedirs(outdir, exist_ok=True)
for i in idx:
    d = rows[i]
    path = os.path.join(outdir, f'{i:02d}.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(d['current'])
    print(i, d['gid'], len(d['current']), path)
