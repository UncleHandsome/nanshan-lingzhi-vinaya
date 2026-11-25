# -*- coding: utf-8 -*-
"""把「句段細配」回覆併入 對位結果_20261125/seg_groups.json。

回覆放這裡：細配材料_20261125/_回/winNN_*.txt（或 .md、.jsonl 皆可）
每行格式：{"B":"1727","A":"575","s":1,"why":"一句依據"}

用法：
  python -X utf8 _src/ingest_seg_replies.py            # 只檢查（dry-run）
  python -X utf8 _src/ingest_seg_replies.py --apply    # 寫回 seg_groups.json

規則：
- 只接受 _清單.json 裡該窗的記段，A 必須是該記段所屬鈔段。
- s 必須是 1..該鈔段句段數，或 "T"/"t"/"tail"。
- 同一鈔段內 s 必須遞增（允許持平；T 最後），違反會列報但整段不寫入。
- 一個鈔段的記段全部到齊才寫入；缺漏的列報，該段暫用預設（全接在最後）。
- 已存在 seg_groups.json 的鈔段（如 575）保留，不被覆蓋。
"""
import argparse
import glob
import io
import json
import os
import re
import sys

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAT = os.path.join(B, '細配材料_20261125')
REPLY = os.path.join(MAT, '_回')
SEGMAP = os.path.join(B, '對位結果_20261125', 'seg_groups.json')
MANIFEST = os.path.join(MAT, '_清單.json')


def norm_s(v, nseg):
    if isinstance(v, str):
        v = v.strip()
        if v.upper() in ('T', 'TAIL', '尾'):
            return 'T'
        if v.isdigit():
            v = int(v)
    if isinstance(v, int):
        if 1 <= v <= nseg:
            return v
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    manifest = json.load(io.open(MANIFEST, encoding='utf-8'))
    ji2row = {}          # 記 key -> (鈔 key, nseg, 窗)
    row_ji = {}          # 鈔 key -> [記 key...] 依記序
    for w in manifest:
        for ck in w['chao']:
            row_ji.setdefault(ck, [])
        pass
    # 由材料本身重建每段的記序
    for w in manifest:
        t = io.open(os.path.join(MAT, w['file']), encoding='utf-8').read()
        cur = None
        for line in t.splitlines():
            m = re.match(r'\[鈔 ([^\]]+)\]（(\d+) 個句段', line)
            if m:
                cur = (m.group(1), int(m.group(2)))
                continue
            m = re.match(r'\[記 ([^\]]+)\]', line)
            if m and cur:
                ji2row[m.group(1)] = (cur[0], cur[1], w['file'])
                row_ji[cur[0]].append(m.group(1))

    files = []
    for pat in ('*.txt', '*.jsonl', '*.md'):
        files += sorted(glob.glob(os.path.join(REPLY, pat)))
    files += sorted(glob.glob(os.path.join(MAT, 'win*_回*.txt')))
    if not files:
        print('沒找到回覆檔。請把回覆放進：', REPLY)
        sys.exit(1)

    rec = {}             # 記 key -> (s, why)
    errs = []
    dup = []
    for p in files:
        t = io.open(p, encoding='utf-8').read().lstrip('\ufeff')
        t = re.sub(r'```[a-zA-Z]*', '', t)
        for ln in t.splitlines():
            ln = ln.strip().lstrip('\ufeff').rstrip(',')
            if not ln.startswith('{'):
                m2 = re.search(r'\{[^{}]*\}', ln)
                if not m2:
                    continue
                ln = m2.group(0)
            try:
                d = json.loads(ln)
            except Exception:
                continue
            k = str(d.get('B', '')).strip()
            if not k:
                continue
            if k in rec:
                dup.append((k, os.path.basename(p)))
                continue
            if k not in ji2row:
                errs.append(('UNKNOWN', k, os.path.basename(p)))
                continue
            ck, nseg, win = ji2row[k]
            a = str(d.get('A', '')).strip()
            if a != ck:
                errs.append(('A_MISMATCH', k, a, ck))
                continue
            s = norm_s(d.get('s'), nseg)
            if s is None:
                errs.append(('BAD_S', k, d.get('s'), 'nseg=%d' % nseg))
                continue
            rec[k] = (s, str(d.get('why', ''))[:60])

    # 已存在的映射（575）
    segmap = {}
    if os.path.exists(SEGMAP):
        segmap = {k: v for k, v in json.load(io.open(SEGMAP, encoding='utf-8')).items()
                  if not k.startswith('_')}

    done_rows = 0
    bad_rows = 0
    for ck, jis in row_ji.items():
        if ck in segmap:
            continue
        got = [j for j in jis if j in rec]
        if not got:
            continue
        nseg = ji2row[jis[0]][1]
        if len(got) != len(jis):
            miss = [j for j in jis if j not in rec]
            errs.append(('INCOMPLETE', ck, '%d/%d' % (len(got), len(jis)), miss[:8]))
            bad_rows += 1
            continue
        ss = [rec[j][0] for j in jis]
        # 遞增檢查
        prev = 0
        ok = True
        for j, s in zip(jis, ss):
            v = 10 ** 6 if s == 'T' else s
            if v < prev:
                errs.append(('ORDER', ck, j, s))
                ok = False
                break
            prev = v
        if not ok:
            bad_rows += 1
            continue
        groups = {}
        tail = []
        for j, s in zip(jis, ss):
            if s == 'T':
                tail.append(j)
            else:
                groups.setdefault(str(s), []).append(j)
        segmap[ck] = dict(segs=nseg, groups=groups)
        if tail:
            segmap[ck]['tail'] = dict(
                note='以上鈔文已盡；以下記文為鈔文無對應之廣釋（或轉入下一段）。',
                keys=tail)
        done_rows += 1

    print('回覆檔 %d 個；解析記段 %d 行；完成鈔段 %d；不完整/違序 %d'
          % (len(files), len(rec), done_rows, bad_rows))
    if dup:
        print('重複（略過）：', dup[:10])
    for e in errs[:20]:
        print(('ERR',) + tuple(e))
    if len(errs) > 20:
        print('…其餘錯誤', len(errs) - 20, '筆')

    if args.apply and done_rows:
        io.open(SEGMAP, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(segmap, ensure_ascii=False, indent=1) + '\n')
        print('已寫入', SEGMAP, '鈔段', len(segmap))
    else:
        print('（dry-run，未寫檔；加 --apply 才寫入）')


if __name__ == '__main__':
    main()
