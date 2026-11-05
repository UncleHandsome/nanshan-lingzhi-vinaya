
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
        secs.append(cur)
        cur = {'title': blk['text'], 'items': []}
        continue
    if blk['kind'] == 'sub' and not cur['items']:
        cur['title'] = blk['text']
        continue
    if blk['kind'] == 'p':
        cur['items'].append(blk['text'])
secs.append(cur)
out = []
for i, s in enumerate(secs):
    n = sum(len(re.findall(r'[\u4e00-\u9fff]', x)) for x in s['items'])
    out.append(f"{i}\t{n}\t{len(s['items'])}\t{s['title'][:50]}")
io.open(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\sections.txt','w',encoding='utf-8').write('\n'.join(out))
print('ok')
