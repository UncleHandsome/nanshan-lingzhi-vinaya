# -*- coding: utf-8 -*-
"""Phase 0：產「文意對位材料」。把行事鈔 30 篇＋序，與資持記對應範圍，
切成大小均衡的子窗，每窗一份材料（鈔段清單＋記段清單），供 subagent 文意對位。
不呼叫任何 AI。輸出 對位材料_20261125/ 與 _windows.json（含大小，供平衡分工）。
"""
import io, json, os, re, math

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '對位材料_20261125')
HAN = re.compile(r'[\u4e00-\u9fff]')
TARGET = 7000  # 每子窗目標合計漢字數

def load(b):
    return [json.loads(x) for x in io.open(os.path.join(B, '定稿', b + '.jsonl'), encoding='utf-8') if x.strip()]

def han(s): return len(HAN.findall(s or ''))

def text_of(r):
    segs = r.get('segments') or []
    if segs:
        return '\n'.join((s.get('display_source') or s.get('source') or '') for s in segs)
    return r.get('display_source') or r.get('source') or ''

chao_bounds = [0,4293,7433,9625,11995,14344,18754,24447,33545,42872,48112,53169,59580,65176,70822,129985,137411,149898,168232,178416,182018,184541,188134,193321,197478,202966,204834,208639,212774,217703,222780,225037]
ji_bounds   = [0,34040,44573,50541,56372,61679,70486,80261,91339,108245,115423,126158,138830,148257,161176,268359,292890,307674,334556,345780,350015,353444,359348,368394,373944,382560,384129,388048,392612,401826,407277,427813]
names = ['序','標宗顯德','集僧通局','足數眾相','受欲是非','通辨羯磨','結界方法','僧網大綱','受戒緣集','師資相攝','說戒正儀','安居策修','自恣宗要','篇聚名報','隨戒釋相','持犯方軌','懺六聚法','二衣總別','四藥受淨','鉢器制聽','對施興治','頭陀行儀','僧像致敬','訃請設則','導俗化方','主客相待','瞻病送終','諸雜要行','沙彌別行','尼眾別行','諸部別行']

def assign(rows, bounds):
    out = [[] for _ in range(len(bounds)-1)]
    for r in rows:
        rs = int(r.get('raw_start') or 0)
        for i in range(len(bounds)-1):
            if bounds[i] <= rs < bounds[i+1]:
                out[i].append(r); break
    return out

HEADER = '''你是南山律典對位員。下面左欄是《行事鈔》某篇的原文段落（鈔段），右欄是《資持記》解釋該篇的原文段落（記段）。
請依「文意」把每個記段對到它所解釋的鈔段，允許：
- 1:1（一個記段對一個鈔段）
- 1:n（一個記段同時解釋多個鈔段）
- n:1（多個記段共同解釋一個鈔段）
- n:m（多對多）
- orphan（記段沒有對應鈔段，例如記的序文、科判總說、卷末校勘）

【判斷依據】讀兩邊原文的語義：記段通常在牒釋（引用並解釋）某個鈔段的詞句。看記段在解哪个鈔段的內容，就對到哪個。不要只看開頭幾個字。
【輸出】只輸出 JSONL，每行一個記段的對位（不要 code fence、前言、解釋）：
{"B":"記段key","A":["鈔段key",...],"type":"1:1|1:n|n:1|n:m|orphan","why":"一句文意依據"}
每個右欄記段都必須輸出一行（含 orphan）。A 為空陣列時 type=orphan。
'''

def split_groups(items, k):
    n = len(items)
    groups = []
    for i in range(k):
        a = n*i//k; b = n*(i+1)//k
        groups.append(items[a:b])
    return groups

def split_by_raw(items, lo, hi, k):
    """依 raw_start 在 [lo,hi) 的位置比例切 k 組（鈔記同進度對齊）。"""
    groups = [[] for _ in range(k)]
    span = hi - lo
    for r in items:
        rs = int(r.get('raw_start') or lo)
        f = (rs - lo) / span if span > 0 else 0
        g = min(k-1, max(0, int(f*k)))
        groups[g].append(r)
    return groups

def ji_anchored_windows(chao, ji, target_ji=40):
    """記文錨定切窗：記文切小組，用每組首/尾記段牒釋詞反查鈔段範圍，
    保證每窗鈔記對應。回傳 [(chao_segs, ji_segs), ...]。"""
    # 鈔段漢字流＋每段起始位置
    ch_han = []; ch_pos = []; acc = 0
    for r in chao:
        t = ''.join(HAN.findall(text_of(r)))
        ch_pos.append(acc); ch_han.append(t); acc += len(t)
    # 鈔文 n-gram 索引 → 鈔段 idx
    NG = 8
    index = {}
    for ci, t in enumerate(ch_han):
        for s in range(len(t)-NG+1):
            index.setdefault(t[s:s+NG], ci)
    def anchor(jr):
        s = ''.join(HAN.findall(text_of(jr)))
        votes = {}
        for p in range(len(s)-NG+1):
            ci = index.get(s[p:p+NG])
            if ci is not None:
                votes[ci] = votes.get(ci, 0)+1
        if not votes: return None
        return max(votes, key=lambda c: (votes[c], -c))
    anchors = [anchor(r) for r in ji]
    MAXSPAN = 34; MAXJI = 40
    wins = []; n = len(ji)
    start = 0; mn = None; mx = None; cnt = 0
    def close(end):
        if end <= start: return
        if mn is None:
            c = int(start/n*len(chao)); lo = max(0, c-5); hi = min(len(chao), c+12)
        else:
            lo = max(0, mn-3); hi = min(len(chao), mx+4)
        wins.append((chao[lo:hi], ji[start:end]))
    for i in range(n):
        a = anchors[i]
        if cnt > 0:
            span_exceed = (a is not None and mn is not None and (max(mx, a)-min(mn, a)) > MAXSPAN)
            if cnt >= MAXJI or span_exceed:
                close(i); start = i; mn = None; mx = None; cnt = 0
        if a is not None:
            mn = a if mn is None else min(mn, a)
            mx = a if mx is None else max(mx, a)
        cnt += 1
    close(n)
    return wins

def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
    x = load('xingshichao'); z = load('zhichi')
    xa = assign(x, chao_bounds); za = assign(z, ji_bounds)
    windows = []
    for i, name in enumerate(names):
        chao = xa[i]; ji = za[i]
        ch = sum(han(text_of(r)) for r in chao)
        jh = sum(han(text_of(r)) for r in ji)
        k = max(1, math.ceil((ch+jh)/TARGET))
        if k > 1:
            pairs = ji_anchored_windows(chao, ji, target_ji=40)
        else:
            pairs = [(chao, ji)]
        nparts = len(pairs)
        for p, (csegs, jsegs) in enumerate(pairs):
            fn = 'pian%02d_%s_part%02d.md' % (i, name, p+1)
            L = [HEADER, '', '## 篇：%s（第 %d/%d 窗）' % (name, p+1, nparts), '',
                 '### 左欄：行事鈔 鈔段（共 %d）' % len(csegs), '']
            for r in csegs:
                L += ['[鈔 %s]' % r['key'], text_of(r), '']
            L += ['### 右欄：資持記 記段（共 %d）' % len(jsegs), '']
            for r in jsegs:
                L += ['[記 %s]' % r['key'], text_of(r), '']
            body = '\n'.join(L)
            io.open(os.path.join(OUT, fn), 'w', encoding='utf-8', newline='\n').write(body)
            windows.append({'file': fn, 'pian': i, 'name': name, 'part': p+1, 'parts': nparts,
                            'chao_n': len(csegs), 'ji_n': len(jsegs),
                            'bytes': len(body.encode('utf-8')),
                            'chao_keys': [str(r['key']) for r in csegs],
                            'ji_keys': [str(r['key']) for r in jsegs]})
    json.dump(windows, io.open(os.path.join(OUT, '_windows.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tot = sum(w['bytes'] for w in windows)
    print('windows', len(windows), 'total MB %.2f' % (tot/1048576), 'avg KB %.1f' % (tot/len(windows)/1024))
    big = sorted(windows, key=lambda w: -w['bytes'])[:5]
    for w in big: print('  largest', w['file'], w['bytes']//1024, 'KB')

if __name__ == '__main__':
    main()
