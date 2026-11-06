# -*- coding: utf-8 -*-
import io, os, re, json
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
out = []

def load(src):
    S = os.path.join(B, 'TXT_分卷', src)
    res = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        res.append((f[:-4], sp))
    return res

for d in ['01_行事鈔', '資持記_細分']:
    S = os.path.join(B, 'TXT_分卷', d)
    files = sorted(os.listdir(S))
    out.append(f'--- {d}: {len(files)} files: ' + ' | '.join(files))

PATS = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
PATS2 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')

def sections():
    secs, cur = [], None
    for k, sp in load('01_行事鈔'):
        for o in sp:
            if PATS2.match(o.strip()):
                continue
            m = PATS.match(o)
            if m:
                if any(x['no'] == m.group(2) for x in secs):
                    cur = next(x for x in secs if x['no'] == m.group(2))
                else:
                    cur = dict(name=m.group(1), no=m.group(2), items=[], file=k)
                    secs.append(cur)
                continue
            if cur is not None:
                cur['items'].append(o)
    return secs

secs = sections()
out.append('=== 鈔 sections ===')
for i, s in enumerate(secs):
    out.append(f'idx{i} 篇{s["no"]} {s["name"]} n={len(s["items"])} file={s["file"]} first={s["items"][0][:40] if s["items"] else ""}')

def zsecs():
    zj = []
    for k, sp in load('資持記_細分'):
        zj += [(k, o) for o in sp]
    ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
    zs, z = [], None
    for k, o in zj:
        if ZP.search(o):
            z = [o]
            zs.append(z)
            continue
        if z is not None:
            z.append(o)
    return zs

zs = zsecs()
out.append('=== 記 sections ===')
tot = 0
for i, z in enumerate(zs):
    out.append(f'idx{i} n={len(z)} start_z={tot} end_z={tot+len(z)-1} head={z[0][:40]}')
    tot += len(z)
out.append(f'total z paragraphs={tot}')
open(os.path.join(AD, '_struct.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
