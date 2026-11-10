# -*- coding: utf-8 -*-
"""解析 batch/round1/resp_001..020.txt，輸出條目 JSON，並比對 out/ 段對齊。"""
import os, io, re, json, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RESP = os.path.join(B, 'batch', 'round1')
MAT = os.path.join(B, '校閱_40K')
OUT = os.path.join(B, 'AI語譯', 'out')
WORK = os.path.join(B, 'AI語譯', '_work', 'review', '_b1')

HDR = re.compile(r'^###\s*[【\[]?([0-9]{3}-[0-9]{4})[】\]]?\s*[｜|]?\s*'
                 r'([^｜|]+?)/([^#｜|]+)#(\d+)\s*[｜|]\s*(P[0-9])\s*[｜|]\s*(.+?)\s*$')


def parse_resp():
    items = []
    for fn in sorted(glob.glob(os.path.join(RESP, 'resp_*.txt'))):
        txt = io.open(fn, encoding='utf-8').read()
        lines = txt.split('\n')
        cur = None
        for ln in lines:
            m = HDR.match(ln.strip())
            if m:
                if cur:
                    items.append(cur)
                cur = dict(file=os.path.basename(fn), gid=m.group(1), book=m.group(2).strip(),
                           chunk=m.group(3).strip(), seg=int(m.group(4)),
                           level=m.group(5), type=m.group(6).strip())
                continue
            if cur is None:
                continue
            s = ln.strip()
            for key, tag in (('quote', '- 原文起首：'), ('problem', '- 問題：'),
                             ('basis', '- 依據：'), ('suggest', '- 建議：'), ('conf', '- 信心：')):
                if s.startswith(tag):
                    cur[key] = s[len(tag):].strip()
        if cur:
            items.append(cur)
    return items


def paras(path):
    txt = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    return [p.strip() for p in re.split(r'\n\s*\n', txt) if p.strip()]


def parse_material(idx):
    """回傳 {gid: (label, src, tr)}"""
    path = os.path.join(MAT, '校閱_%03d.txt' % idx)
    txt = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    out = {}
    blocks = re.split(r'\n\s*\n', txt)
    cur = None
    for b in blocks:
        ms = re.findall(r'【([0-9]{3}-[0-9]{4})】([^\n]*)', b)
        if ms:
            gid, label = ms[0]
            src = re.search(r'【原文】(.*?)(?=【譯文】|\Z)', b, re.S)
            tr = re.search(r'【譯文】(.*)\Z', b, re.S)
            out[gid] = (label.strip(), (src.group(1).strip() if src else ''),
                        (tr.group(1).strip() if tr else ''))
    return out


def main():
    items = parse_resp()
    print('解析條目數：', len(items))
    # 分檔讀材料
    mats = {}
    for i in range(1, 21):
        mats[i] = parse_material(i)
    books = {}
    for it in items:
        it['matfile'] = int(it['gid'].split('-')[0])
        key = it['matfile']
        it['mat'] = mats[key].get(it['gid'], None)
    json.dump(items, io.open(os.path.join(WORK, 'items.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    # 對齊檢查：材料譯文 vs out 段落
    cache = {}
    ok = bad = 0
    for it in items:
        if not it['mat']:
            print('!! 材料缺', it['gid']); bad += 1; continue
        label = it['mat'][0]
        lab = label.replace('】', '').replace('【', '').strip()
        m = re.match(r'(.+?)/(.+)#(\d+)$', lab)
        if not m:
            print('!! 標籤異常', label); bad += 1; continue
        bk, ck, sg = m.group(1), m.group(2), int(m.group(3))
        it['book2'], it['chunk2'], it['seg2'] = bk, ck, sg
        if bk != it['book'] or ck != it['chunk'] or sg != it['seg']:
            print('!! 標籤與材料不一致', it['gid'], it['book'], it['chunk'], it['seg'], '|', lab)
        p = os.path.join(OUT, bk, ck + '.txt')
        if bk not in cache:
            cache[bk] = {}
        if ck not in cache[bk]:
            cache[bk][ck] = paras(p)
        ps = cache[bk][ck]
        it['npara'] = len(ps)
        it['cur'] = ps[sg - 1] if 0 < sg <= len(ps) else ''
        mat_tr = re.sub(r'\s+', '', it['mat'][2])
        cur_tr = re.sub(r'\s+', '', it['cur'])
        if mat_tr == cur_tr:
            ok += 1
        else:
            bad += 1
            it['mis'] = (mat_tr[:400], cur_tr[:400])
    print('材料譯文 == out 段落：', ok, ' 不等：', bad)
    json.dump(items, io.open(os.path.join(WORK, 'items.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    for it in items:
        if 'mis' in it:
            print('\n=== 不等', it['gid'], it['book'], it['chunk'], it['seg'], 'npara=', it['npara'])
            print(' MAT:', it['mis'][0][:250])
            print(' CUR:', it['mis'][1][:250])


if __name__ == '__main__':
    main()
