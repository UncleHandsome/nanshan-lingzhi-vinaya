
import sys, os, io, re, json
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src')
import build
build.RAW = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\xml'
b = [x for x in build.BOOKS if x['key']=='01'][0]
blocks = build.tidy_blocks(build.parse_book(b))
secs = []
cur = {'title': '序', 'items': []}
for blk in blocks:
    if blk['kind'] == 'juan':
        continue
    if blk['kind'] == 'head':
        secs.append(cur); cur = {'title': blk['text'], 'items': []}; continue
    if blk['kind'] == 'sub' and not cur['items']:
        cur['title'] = blk['text']; continue
    if blk['kind'] == 'p':
        cur['items'].append(blk['text'])
secs.append(cur)
io.open(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\secs.json','w',encoding='utf-8').write(json.dumps(secs, ensure_ascii=False))
lines = []
for i, s in enumerate(secs[:4]):
    lines.append('===== SECTION %d : %s (%d paras) =====' % (i, s['title'], len(s['items'])))
    for j, it in enumerate(s['items']):
        lines.append('[%d.%d] %s' % (i, j+1, it))
io.open(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\dump.txt','w',encoding='utf-8').write('\n'.join(lines))
print('done', len(secs))
