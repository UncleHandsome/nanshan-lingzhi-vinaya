# -*- coding: utf-8 -*-
"""產「orphan 補漏」材料（可直接丟給外部 AI；本腳本不呼叫 AI）。

每篇一份材料：
  1. 該篇《行事鈔》鈔段全文（左欄，供對照）
  2. 待判定的記段（全文）＋前後已對位結果
檔頭附提示詞，AI 回 JSONL 即可。

輸出：對位結果_20261125/orphan_補漏材料_<篇>.md
      對位結果_20261125/orphan_補漏材料.md（全部合併）
"""
import glob
import io
import json
import os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '對位材料_20261125')
RES = os.path.join(B, '定稿', '對位結果_20261125')
HAN_LIMIT = 10 ** 9        # 一律放該篇鈔文全文（使用者指定）
NEAR = 40                  # 附近段數


def load(book):
    return {str(json.loads(x)['key']): json.loads(x)
            for x in io.open(os.path.join(B, '定稿', book + '.jsonl'), encoding='utf-8') if x.strip()}


def txt(r):
    segs = r.get('segments') or []
    if segs:
        return '\n'.join((s.get('display_source') or s.get('source') or '') for s in segs)
    return r.get('display_source') or r.get('source') or ''


HEAD = '''你是南山律典對位員。《行事鈔》（鈔，道宣）是母本；《資持記》（記，元照）逐段解釋鈔文。
下面會給某篇的【鈔段全文】，再給幾個【判為 orphan 的記段】（上一輪找不到對應鈔段，很可能判錯）。
請依文意判斷每個記段實際在解釋哪個／哪些鈔段。

【輸出】只輸出 JSONL，每行一筆，key 用題目給的記段 key：
{"key":"記段key","A":["鈔段key",...],"note":"一句依據"}
- A 可多個（1:n、n:m）
- 若確定真無對應鈔段（卷首標題、科判總說、卷末校勘），A=[]
- 每筆都要一行，不要 code fence、不要前言
'''


def main():
    wins = {w['file'][:-3]: w for w in
            json.load(io.open(os.path.join(MAT, '_windows.json'), encoding='utf-8'))}
    chao = load('xingshichao'); ji = load('zhichi')
    EMPTY_JI = {k for k, r in ji.items() if not (r.get('translation') or '').strip()}
    # 篇 -> 該篇全部鈔段（取各窗聯集，保持順序）
    pian_chao = {}
    pian_name = {}
    for w in wins.values():
        i = w['pian']
        pian_name[i] = w['name']
        lst = pian_chao.setdefault(i, [])
        for k in w['chao_keys']:
            if k not in lst:
                lst.append(k)
    items = []
    for p in sorted(glob.glob(os.path.join(RES, 'pian*.jsonl'))):
        stem = os.path.basename(p)[:-6]
        win = wins.get(stem)
        if not win:
            continue
        lines = [json.loads(l) for l in io.open(p, encoding='utf-8') if l.strip()]
        for i, o in enumerate(lines):
            if o.get('A'):
                continue          # 有對位就不算 orphan（不論 type 寫什麼）
            if str(o.get('B')) in EMPTY_JI:      # 校勘異體字表：不譯、不對位
                continue
            if o.get('reviewed'):                # 已人工判定
                continue
            prev_o = next_o = None
            for j in range(i - 1, -1, -1):
                if lines[j].get('A'):
                    prev_o = lines[j]; break
            for j in range(i + 1, len(lines)):
                if lines[j].get('A'):
                    next_o = lines[j]; break
            items.append({'pian': win['pian'], 'name': win['name'], 'file': stem,
                          'B': o['B'], 'src': txt(ji.get(str(o['B']))),
                          'prev': (prev_o['B'], prev_o['A']) if prev_o else None,
                          'next': (next_o['B'], next_o['A']) if next_o else None})

    by = {}
    for b in items:
        by.setdefault(b['pian'], []).append(b)

    def render(group, pian):
        name = pian_name.get(pian, '')
        ck = pian_chao.get(pian, [])
        tot_han = sum(len(txt(chao[k])) for k in ck if k in chao)
        L = [HEAD, '# 篇：%s' % name, '']
        if tot_han <= HAN_LIMIT:
            L += ['## 一、本篇《行事鈔》鈔段全文（%d 段，%d 字）' % (len(ck), tot_han), '']
            for k in ck:
                if k in chao:
                    L += ['[鈔 %s]' % k, txt(chao[k]), '']
        else:
            # 大型篇：只放 orphan 附近的鈔段
            cpos = {k: i for i, k in enumerate(ck)}
            near = set()
            for b in group:
                for src in (b['prev'], b['next']):
                    if not src:
                        continue
                    for ak in src[1]:
                        ci = cpos.get(ak)
                        if ci is not None:
                            near |= set(range(max(0, ci - NEAR), min(len(ck), ci + NEAR)))
            if not near:
                near = set(range(min(len(ck), 2 * NEAR)))
            idx = sorted(near)
            L += ['## 一、本篇《行事鈔》鈔段（節錄 orphan 附近 %d 段／全篇 %d 段）'
                  % (len(idx), len(ck)), '']
            for ci in idx:
                k = ck[ci]
                if k in chao:
                    L += ['[鈔 %s]' % k, txt(chao[k]), '']
        L += ['## 二、待判定的記段（%d 筆）' % len(group), '']
        for n, b in enumerate(group, 1):
            L += ['---', '', '### [%d] 記 %s' % (n, b['B']), '', b['src'], '']
            if b['prev']:
                L += ['前已對位：記 %s → 鈔 %s' % (b['prev'][0], ','.join(b['prev'][1])), '']
            if b['next']:
                L += ['後已對位：記 %s → 鈔 %s' % (b['next'][0], ','.join(b['next'][1])), '']
        return '\n'.join(L)

    allparts = []
    for pian, group in sorted(by.items()):
        body = render(group, pian)
        fn = os.path.join(RES, 'orphan_補漏材料_%s.md' % pian_name.get(pian, pian))
        io.open(fn, 'w', encoding='utf-8', newline='\n').write(body)
        print('  %-14s %2d 筆  %3d KB' % (pian_name.get(pian, pian), len(group),
                                         os.path.getsize(fn) // 1024))
        allparts.append(body)
    comb = os.path.join(RES, 'orphan_補漏材料.md')
    io.open(comb, 'w', encoding='utf-8', newline='\n').write('\n\n'.join(allparts))
    print('合併 %d 篇 %d 筆 → %s（%d KB）' % (len(by), len(items), os.path.basename(comb),
                                            os.path.getsize(comb) // 1024))


if __name__ == '__main__':
    main()
