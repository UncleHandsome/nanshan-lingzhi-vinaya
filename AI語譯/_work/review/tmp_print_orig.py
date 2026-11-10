import json

rows = json.load(open(r'AI語譯\_work\review\tmp_g3_rows.json', encoding='utf-8'))
out = []
for i in (21, 26, 28, 29, 35, 39, 40):
    d = rows[i]
    out.append('=' * 30)
    out.append(f'[{i}] {d["gid"]} seg={d["seg"]}')
    out.append('ORIG: ' + d['orig'])
open(r'AI語譯\_work\review\tmp_g3_orig.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
