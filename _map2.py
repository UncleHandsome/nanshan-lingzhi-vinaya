import re, os, json

files = [181,188,192,226,277,392,413,441,448,472,473,475,477,479,480,481,551]

def parse_jiao(n):
    p = os.path.join('校閱_10K', f'校閱_{n:03d}.txt')
    s = open(p, encoding='utf-8-sig').read()
    segs = []
    for m in re.finditer(r'【(\d{3}-\d{4})】(\S+?)#(\d+)\r?\n【原文】(.*?)\r?\n【譯文】(.*?)(?=\r?\n\r?\n【|\Z)', s, re.S):
        segs.append(dict(id=m.group(1), book=m.group(2).split('/')[0], chunk=m.group(2).split('/')[1],
                         para=int(m.group(3)), src_text=m.group(4).strip(), trans=m.group(5).strip()))
    return segs

out = []
for n in files:
    segs = parse_jiao(n)
    print('='*20, n, 'segs', len(segs))
    for sg in segs:
        path = os.path.join('AI語譯','out',sg['book'],sg['chunk']+'.txt')
        s = open(path, encoding='utf-8-sig').read()
        blocks = re.split(r'\r?\n\r?\n', s.strip())
        # careful: split on blank lines
        cur = blocks[sg['para']-1] if sg['para']-1 < len(blocks) else None
        same = (cur == sg['trans']) if cur is not None else None
        print(f"{sg['id']} {sg['book']}/{sg['chunk']}#{sg['para']} len_cur={len(cur) if cur else 0} len_old={len(sg['trans'])} same={same}")
        out.append(dict(num=n, id=sg['id'], book=sg['book'], chunk=sg['chunk'], para=sg['para'],
                        cur=cur, old=sg['trans'], src=sg['src_text']))
json.dump(out, open('_map.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
