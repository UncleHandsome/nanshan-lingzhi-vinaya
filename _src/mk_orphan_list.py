# -*- coding: utf-8 -*-
"""產生「orphan 待人工對位」清單（不呼叫任何 AI）。

對 對位結果_20261125/*.jsonl 裡 type=orphan 的記段，輸出：
  對位_orphan_待人工.md
每筆含：記段 key、原文、前後已對位的記段（及其鈔段）、候選鈔段原文、待填欄位。

使用者直接在這份 md 上填，或另存 JSONL 後用 ingest 方式回填。
"""
import glob
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '對位材料_20261125')
RES = os.path.join(B, '定稿', '對位結果_20261125')
OUT = os.path.join(RES, 'orphan_待人工.md')
HAN = re.compile(r'[\u4e00-\u9fff]')


def load(book):
    return {str(json.loads(x)['key']): json.loads(x)
            for x in io.open(os.path.join(B, '定稿', book + '.jsonl'), encoding='utf-8') if x.strip()}


def txt(r):
    segs = r.get('segments') or []
    if segs:
        return '\n'.join((s.get('display_source') or s.get('source') or '') for s in segs)
    return r.get('display_source') or r.get('source') or ''


def main():
    wins = {w['file'][:-3]: w for w in
            json.load(io.open(os.path.join(MAT, '_windows.json'), encoding='utf-8'))}
    chao = load('xingshichao'); ji = load('zhichi')
    EMPTY_JI = {k for k, r in ji.items() if not (r.get('translation') or '').strip()}
    blocks = []
    total = 0
    for p in sorted(glob.glob(os.path.join(RES, 'pian*.jsonl'))):
        stem = os.path.basename(p)[:-6]
        win = wins.get(stem)
        if not win:
            continue
        lines = [json.loads(l) for l in io.open(p, encoding='utf-8') if l.strip()]
        ckeys = win['chao_keys']
        cpos = {k: i for i, k in enumerate(ckeys)}
        for i, o in enumerate(lines):
            if o.get('A'):
                continue          # 有對位就不算 orphan（不論 type 寫什麼）
            if str(o.get('B')) in EMPTY_JI:      # 校勘異體字表：不譯、不對位
                continue
            if o.get('reviewed'):                # 已人工判定
                continue
            total += 1
            prev_a = []; next_a = []
            for j in range(i - 1, -1, -1):
                if lines[j].get('A'):
                    prev_a = lines[j]['A']; break
            for j in range(i + 1, len(lines)):
                if lines[j].get('A'):
                    next_a = lines[j]['A']; break
            cand = []
            for k in prev_a + next_a:
                ci = cpos.get(k)
                if ci is not None:
                    cand += ckeys[max(0, ci - 2): ci + 3]
            cand = [k for k in dict.fromkeys(cand)][:12] or ckeys[:12]
            jr = ji.get(str(o['B']))
            blocks.append({
                'no': total, 'file': stem, 'name': win['name'],
                'B': o['B'], 'src': txt(jr) if jr else '',
                'prev': prev_a, 'next': next_a,
                'cand': [(k, txt(chao[k]) if k in chao else '') for k in cand],
                'why': o.get('why') or '',
            })
    L = ['# 對位 orphan 待人工判定（%d 筆）' % total, '',
         '每筆只要回答：這記段對到哪些鈔段（可用多個）、或確定是 orphan。',
         '格式（存成 JSONL 後交給 ingest_user_reply.py 同樣流程）：',
         '```json',
         '{"key":"記段key","status":"fixed","translation":"","A":["鈔段key"],"note":"依據"}',
         '```', '']
    for b in blocks:
        L += ['---', '',
              '## [%d] %s／記 %s（%s）' % (b['no'], b['name'], b['B'], b['file']), '',
              '**記段原文**：', '', b['src'], '']
        if b['prev'] or b['next']:
            L += ['**前後已對位**：前 → %s｜後 → %s' % (
                ','.join(b['prev']) or '（無）', ','.join(b['next']) or '（無）'), '']
        L += ['**候選鈔段**：', '']
        for k, t in b['cand']:
            L += ['- `%s` %s' % (k, t.replace('\n', ' ')[:160]), '']
        L += ['**待填**：A = ________｜type = ________｜依據 = ________', '']
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
    print('orphan %d 筆 → %s' % (total, OUT))


if __name__ == '__main__':
    main()
