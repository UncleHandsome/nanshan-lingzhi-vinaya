# -*- coding: utf-8 -*-
"""細配材料：把「多句段鈔段」與其名下記段整理成給 AI 的句中對位材料。

產出 細配材料_20261125/：
  _提示詞.md          任務規則＋範例（575 已完成的映射）
  winNN_*.md          每窗 ≤ 約 12K 漢字的材料
  _清單.json          窗→(卷, 鈔 key, 記 key) 範圍，供回填核對

用法：
  python -X utf8 _src/build_seg_materials.py            # 產生材料
  python -X utf8 _src/build_seg_materials.py --stats    # 只印統計
"""
import argparse
import glob
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import site_hebian as SH

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(B, '細配材料_20261125')
SEGMAP = os.path.join(B, '定稿', '對位結果_20261125', 'seg_groups.json')
TARGET_HAN = 12000  # 每窗大約漢字數


def han(s):
    return ''.join(ch for ch in s if '\u3400' <= ch <= '\u9fff')


def seg_texts(row):
    out = []
    for s in row.get('segments') or []:
        src = s.get('display_source') or s.get('source') or ''
        if han(src):
            out.append(src.strip())
    if not out:
        out = [(row.get('display_source') or row.get('source') or '').strip()]
    return [x for x in out if x]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stats', action='store_true')
    args = ap.parse_args()

    hraw, bounds = SH.volume_bounds()
    chao, titles = SH.build_chao(SH.load_jsonl('xingshichao'), hraw, bounds)
    ji, _ = SH.build_ji(SH.load_jsonl('zhichi'))
    idx = json.load(io.open(os.path.join(B, '定稿', '對位結果_20261125', 'pairs_v2_index.json'),
                            encoding='utf-8'))
    c2j = idx['chao2ji']
    ji2c = idx['ji2chao']

    # 與 site_hebian2 相同的落點規則：記段歸到書中位置最前面的鈔段
    rows = {}          # key -> dict(row, segs, unit_seqs, pos, vol, chapter)
    key_pos = {}
    key_last_seq = {}
    for u in chao:
        k = str(u['key'])
        rows.setdefault(k, u)
        key_pos.setdefault(k, u['pos'])
        key_last_seq[k] = max(key_last_seq.get(k, 0), u['seq'])
    ji_by_key = {}
    for i, u in enumerate(ji):
        ji_by_key.setdefault(str(u['key']), []).append(i)
    chao_keys = set(rows)

    owner = {}
    for i, u in enumerate(ji):
        k = str(u['key'])
        targets = [t for t in (ji2c.get(k) or []) if t in chao_keys]
        if not targets:
            continue
        owner[i] = min(targets, key=lambda x: key_pos.get(x, 1 << 30))

    # 多句段鈔段 → 名下記段（依記序）
    xrows = {str(r['key']): r for r in SH.load_jsonl('xingshichao')}
    multi = []
    for k in sorted(rows, key=lambda x: key_pos.get(x, 1 << 30)):
        u = rows[k]
        nseg = key_last_seq[k] + 1
        if nseg <= 1 or k not in xrows:
            continue
        mine = sorted(i for i, o in owner.items() if o == k)
        multi.append(dict(key=k, vol=u['vol'], chapter=u['chapter'], pos=u['pos'],
                          nseg=nseg, segs=seg_texts(xrows[k]),
                          ji=[(str(ji[i]['key']), ji[i].get('source', '')) for i in mine]))
    multi = [m for m in multi if m['ji']]
    n_ji = sum(len(m['ji']) for m in multi)
    n_han = sum(len(han(''.join(m['segs']))) + sum(len(han(s)) for _, s in m['ji'])
                for m in multi)
    print('多句段鈔段（有記段）:', len(multi), ' 記段:', n_ji, ' 漢字約:', n_han,
          ' 預估窗數:', (n_han + TARGET_HAN - 1) // TARGET_HAN)
    if args.stats:
        for m in multi[:15]:
            print('  鈔 %-8s segs=%d ji=%d vol=%s' % (m['key'], m['nseg'], len(m['ji']), m['vol']))
        return

    # 已完成的不再出題（575 當範例）
    done = {}
    if os.path.exists(SEGMAP):
        done = {k: v for k, v in json.load(io.open(SEGMAP, encoding='utf-8')).items()
                if not k.startswith('_')}
    todo = [m for m in multi if m['key'] not in done]

    # 分窗：不切開同一個鈔段的記段組
    windows = []
    cur, cur_han = [], 0
    for m in todo:
        h = len(han(''.join(m['segs']))) + sum(len(han(s)) for _, s in m['ji'])
        if cur and cur_han + h > TARGET_HAN:
            windows.append(cur)
            cur, cur_han = [], 0
        cur.append(m)
        cur_han += h
    if cur:
        windows.append(cur)

    os.makedirs(OUTDIR, exist_ok=True)
    for f in glob.glob(os.path.join(OUTDIR, '*.md')):
        os.remove(f)

    # 範例（575）——已完成，附在提示詞
    ex = next((m for m in multi if m['key'] == '575'), None)
    ex_preview = ''
    if ex:
        ex_preview = '\n'.join('%d. %s' % (si, src[:34] + ('…' if len(src) > 34 else ''))
                               for si, src in enumerate(ex['segs'], 1))

    prompt = '''你是南山律典「句段細配」員。下面材料是《行事鈔》的若干鈔段，每個鈔段已切成數個「句段」（以 1. 2. 3. …編號）；接著列出《資持記》解釋這個鈔段的記段（依原書順序）。

請判斷「每一個記段主要在解釋哪一個句段」，只輸出 JSONL，每行一個記段：
{"B":"記段key","A":"鈔段key","s":句段序號,"why":"一句依據"}

【s 規則】
- s 用句段前面的編號（1、2、3…）。
- 記段內容若在最後一句段之後、鈔文已經沒有對應文字（例如廣引《業疏》正義、勸學、卷末校勘），s 用 "T"（tail）。
- 每個記段只能給一個 s。
- 記段順序＝鈔句段順序：前面的記段 s 不得大於後面的記段 s（只能持平或遞增；"T" 一定在最後）。若某記段跨前後兩句，取它「主要」解釋的那一句；不要為了方便而平均分配。
- 一句鈔文可以連續掛很多段記文（甚至十幾段）；句段短不代表記段少。

【判斷依據】
- 記段通常在開頭牒釋（引用、科判）它所解釋的鈔句：例如「示宗中，初句通示異計」＝在講鈔句「二論不同…」。
- 記段裡的「」引文可直接拿去找對應的鈔句段。
- 要讀整段文意，不要只看開頭兩個字，也不要按字數比例切。

【範例：鈔 575「三出體狀」已完成（本題不再重複出，只示範粒度）】
鈔 575 的 7 個句段：
''' + ex_preview + '''
正確落點（節錄）：
{"B":"1727","A":"575","s":1,"why":"釋「二論不同；今依本宗」"}
{"B":"1728","A":"575","s":1,"why":"辨空有二宗"}
{"B":"1733","A":"575","s":2,"why":"續名色義，轉入「先明作戒體」"}
{"B":"1738","A":"575","s":3,"why":"釋「相續善色聲，法入所攝」"}
{"B":"1743","A":"575","s":4,"why":"釋「非色者，非塵大所成」"}
{"B":"1754","A":"575","s":7,"why":"釋《涅槃》《十住》證非色"}
{"B":"1756","A":"575","s":"T","why":"鈔文已盡，廣引《業疏》明有宗"}

【輸出】只輸出 JSONL，每行一個記段，依材料中記段出現的順序輸出；不要 code fence、不要前言、不要總結。材料中每個記段都必須輸出一行，最後一行的數目要等於「本窗記段合計」。
'''
    io.open(os.path.join(OUTDIR, '_提示詞.md'), 'w', encoding='utf-8',
            newline='\n').write(prompt)

    manifest = []
    for wi, ws in enumerate(windows, 1):
        vol0, vol1 = ws[0]['vol'], ws[-1]['vol']
        volpart = vol0 if vol0 == vol1 else '%s～%s' % (vol0, vol1)
        name = 'win%02d_%s' % (wi, volpart)
        lines = [prompt, '\n---\n']
        keys = []
        for m in ws:
            lines.append('\n[鈔 %s]（%d 個句段，記段 %d）' %
                         (m['key'], m['nseg'], len(m['ji'])))
            for si, src in enumerate(m['segs'], 1):
                lines.append('%d. %s' % (si, src))
            lines.append('記段：')
            for jk, jsrc in m['ji']:
                lines.append('[記 %s] %s' % (jk, jsrc))
                keys.append(jk)
        lines.append('\n【本窗記段合計 %d 個，輸出必須剛好 %d 行】' % (len(keys), len(keys)))
        io.open(os.path.join(OUTDIR, name + '.md'), 'w', encoding='utf-8',
                newline='\n').write('\n'.join(lines) + '\n')
        manifest.append(dict(file=name + '.md', n_chao=len(ws), n_ji=len(keys),
                             chao=[m['key'] for m in ws], ji=keys,
                             han=sum(len(han(''.join(m['segs']))) +
                                     sum(len(han(s)) for _, s in m['ji']) for m in ws)))
        print('%-24s 鈔 %2d 記 %3d 漢字 %5d' % (name, len(ws), len(keys), manifest[-1]['han']))
    io.open(os.path.join(OUTDIR, '_清單.json'), 'w', encoding='utf-8', newline='\n').write(
        json.dumps(manifest, ensure_ascii=False, indent=1) + '\n')
    print('窗數', len(windows), '記段合計', sum(x['n_ji'] for x in manifest))


if __name__ == '__main__':
    main()
