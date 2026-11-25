# -*- coding: utf-8 -*-
"""合併 37 窗對位結果 → pairs_v2.jsonl ＋ 統計 ＋ 覆蓋率檢查。

輸入：對位結果_20261125/pian*.jsonl（每行 {"B":記段,"A":[鈔段...],"type","why"}）
輸出：
  對位結果_20261125/pairs_v2.jsonl        每行一個 pair 方向（鈔→記 與 記→鈔）
  對位結果_20261125/pairs_v2_index.json   {chao: {key:[記...]}, ji: {key:[鈔...]}}
  對位結果_20261125/pairs_v2_統計.md      統計與覆蓋率報告
不呼叫 AI、不改 定稿/。
"""
import glob
import io
import json
import os
import re
import collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RES = os.path.join(B, '對位結果_20261125')
MAT = os.path.join(B, '對位材料_20261125')
OUT_JSONL = os.path.join(RES, 'pairs_v2.jsonl')
OUT_IDX = os.path.join(RES, 'pairs_v2_index.json')
OUT_MD = os.path.join(RES, 'pairs_v2_統計.md')

chao_bounds = [0,4293,7433,9625,11995,14344,18754,24447,33545,42872,48112,53169,59580,65176,70822,129985,137411,149898,168232,178416,182018,184541,188134,193321,197478,202966,204834,208639,212774,217703,222780,225037]
ji_bounds = [0,34040,44573,50541,56372,61679,70486,80261,91339,108245,115423,126158,138830,148257,161176,268359,292890,307674,334556,345780,350015,353444,359348,368394,373944,382560,384129,388048,392612,401826,407277,427813]
names = ['序','標宗顯德','集僧通局','足數眾相','受欲是非','通辨羯磨','結界方法','僧網大綱','受戒緣集','師資相攝','說戒正儀','安居策修','自恣宗要','篇聚名報','隨戒釋相','持犯方軌','懺六聚法','二衣總別','四藥受淨','鉢器制聽','對施興治','頭陀行儀','僧像致敬','訃請設則','導俗化方','主客相待','瞻病送終','諸雜要行','沙彌別行','尼眾別行','諸部別行']


def load(book):
    return {str(json.loads(x)['key']): json.loads(x)
            for x in io.open(os.path.join(B, '定稿', book + '.jsonl'), encoding='utf-8') if x.strip()}


def pian_of_chao(key):
    r = load_cache['x']['chao'].get(key)
    if not r:
        return None
    p = int(r.get('raw_start') or 0)
    for i in range(len(chao_bounds) - 1):
        if chao_bounds[i] <= p < chao_bounds[i + 1]:
            return i
    return None


load_cache = {}


def main():
    load_cache['x'] = {'chao': load('xingshichao')}
    ji = load('zhichi')
    wins = {w['file'][:-3]: w for w in
            json.load(io.open(os.path.join(MAT, '_windows.json'), encoding='utf-8'))}

    chao2ji = collections.defaultdict(list)
    ji2chao = collections.defaultdict(list)
    typec = collections.Counter()
    per_pian = collections.Counter()
    orphan_reviewed = collections.Counter()
    orphan_list = []
    empty_ji = {k for k, r in ji.items() if not (r.get('translation') or '').strip()}

    for p in sorted(glob.glob(os.path.join(RES, 'pian*.jsonl'))):
        stem = os.path.basename(p)[:-6]
        win = wins.get(stem)
        if not win:
            continue
        piano = win['pian']
        for ln in io.open(p, encoding='utf-8'):
            if not ln.strip():
                continue
            o = json.loads(ln)
            b = str(o.get('B') or '').strip()
            a = [str(x).strip() for x in (o.get('A') or [])]
            t = str(o.get('type') or '').strip()
            typec[t or '?'] += 1
            if not a:
                if b in empty_ji:
                    orphan_reviewed['校勘表(不譯)'] += 1
                elif o.get('reviewed'):
                    orphan_reviewed['已人工判定'] += 1
                else:
                    orphan_reviewed['未判'] += 1
                orphan_list.append((piano, b, o.get('why') or ''))
                continue
            ji2chao[b] = a
            for c in a:
                chao2ji[c].append(b)
            per_pian[piano] += 1

    # 輸出 jsonl（兩個方向）
    with io.open(OUT_JSONL, 'w', encoding='utf-8', newline='\n') as f:
        for c in sorted(chao2ji):
            f.write(json.dumps({'chao': c, 'ji': sorted(chao2ji[c]),
                                'n_ji': len(chao2ji[c])}, ensure_ascii=False) + '\n')
        for b in sorted(ji2chao):
            f.write(json.dumps({'ji': b, 'chao': sorted(ji2chao[b]),
                                'n_chao': len(ji2chao[b])}, ensure_ascii=False) + '\n')
    idx = {'chao2ji': {k: sorted(v) for k, v in chao2ji.items()},
           'ji2chao': {k: sorted(v) for k, v in ji2chao.items()}}
    io.open(OUT_IDX, 'w', encoding='utf-8').write(json.dumps(idx, ensure_ascii=False, indent=1))

    # 覆蓋率：只算「有譯文的鈔段」（排除空白/非正文）
    chao_rows = load_cache['x']['chao']
    chao_total = [k for k, r in chao_rows.items()
                  if (r.get('translation') or '').strip() or (r.get('source') or '').strip()]
    covered = [k for k in chao_total if k in chao2ji]
    uncovered = [k for k in chao_total if k not in chao2ji]

    L = ['# pairs_v2 統計', '',
         '## 總量', '',
         '```text',
         '記段總數      %d' % len(ji),
         '有對位的記段  %d' % len(ji2chao),
         '鈔段（有被對到）%d' % len(chao2ji),
         'orphan 記段   %d' % sum(orphan_reviewed.values()),
         '```', '',
         '## 型別分布', '', '```text']
    for k, v in typec.most_common():
        L.append('%-8s %d' % (k, v))
    L += ['```', '', '## orphan 分類', '', '```text']
    for k, v in orphan_reviewed.most_common():
        L.append('%-14s %d' % (k, v))
    L += ['```', '', '## 每篇 pair 數（記段被對到的數量）', '', '```text']
    for i, nm in enumerate(names):
        L.append('%-8s %d' % (nm, per_pian.get(i, 0)))
    L += ['```', '', '## 鈔段覆蓋率', '', '```text',
          '鈔段總數          %d' % len(chao_total),
          '有記段對到        %d' % len(covered),
          '沒有記段對到      %d' % len(uncovered),
          '覆蓋率            %.1f%%' % (len(covered) * 100.0 / max(1, len(chao_total))),
          '```', '']
    if uncovered:
        L += ['### 未被任何記段對到的鈔段（前 60 筆）', '', '```text']
        for k in uncovered[:60]:
            src = (chao_rows[k].get('source') or '')[:36].replace('\n', ' ')
            L.append('%-10s %s' % (k, src))
        L += ['```', '']
    io.open(OUT_MD, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))

    print('記段 %d，有對位 %d，orphan %d' % (len(ji), len(ji2chao), sum(orphan_reviewed.values())))
    print('鈔段被對到 %d 個；覆蓋率 %.1f%%（%d/%d）' % (
        len(chao2ji), len(covered) * 100.0 / max(1, len(chao_total)), len(covered), len(chao_total)))
    print('輸出：pairs_v2.jsonl / pairs_v2_index.json / pairs_v2_統計.md')


if __name__ == '__main__':
    main()
