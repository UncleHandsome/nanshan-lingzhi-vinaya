# -*- coding: utf-8 -*-
import json
d = [json.loads(l) for l in open('_r2z4_doubts.jsonl', encoding='utf-8')]
seen = set(); du = []
for x in d:
    k = (x.get('resp'), x.get('seg'), x.get('q'))
    if k in seen: continue
    seen.add(k); du.append(x)
for l in open('_r2z4_rejects.jsonl', encoding='utf-8'):
    x = json.loads(l)
    if x['cat'] == '存疑':
        du.append({'resp': x['resp'], 'seg': x['seg'], 'q': '', 'note': x['note']})
du.sort(key=lambda x: (int(x['resp']), str(x.get('seg'))))
lines = ['', '---', '', '# r2 資持記 存疑（resp_926–999，02b–04b 上三，第四輪）', '',
         '本節 73 條。逐條均已回查原文；因異文、句讀或所指未定，暫不改動，保留原譯或已作折中處理。', '']
for i, x in enumerate(du, 1):
    q = '「%s」' % x['q'] if x.get('q') else ''
    lines.append('%d. **%s-%s %s**：%s' % (i, x['resp'], x.get('seg', ''), q, x['note']))
open('_r2z4_doubts.md', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote', len(du))
