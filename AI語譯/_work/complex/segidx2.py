# -*- coding: utf-8 -*-
"""Rebuild segment index over the material files actually covered by the batch (1..578)."""
import re, os, json, glob
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
sys_path = OUT

def _num(p):
    m = re.search(r'(\d+)\.txt$', p)
    return int(m.group(1)) if m else 0

def main():
    labels, codes = {}, {}
    maxn = max(int(re.search(r'resp_(\d+)', f).group(1))
               for f in glob.glob(os.path.join(ROOT, 'batch_qwen', 'r1_complex', 'resp_*.txt')))
    files = [f for f in glob.glob(os.path.join(ROOT, '校閱_10K', '校閱_*.txt')) if 1 <= _num(f) <= maxn]
    files.sort(key=_num)
    for mf in files:
        t = open(mf, encoding='utf-8').read()
        i = t.find('# 材料開始')
        if i < 0:
            continue
        seg = t[i:]
        parts = re.split(r'(?m)^【(\d{3}-\d{4})】(.+)$', seg)
        for j in range(1, len(parts), 3):
            code, label, body = parts[j], parts[j + 1].strip(), parts[j + 2]
            om = re.search(r'【原文】(.*?)(?=【譯文】|\Z)', body, re.S)
            tm = re.search(r'【譯文】(.*)', body, re.S)
            rec = {'code': code, 'label': label,
                   'src': (om.group(1).strip() if om else ''),
                   'tr': (tm.group(1).strip() if tm else ''),
                   'mat': os.path.basename(mf)}
            labels[label] = rec
            codes[code] = rec
    json.dump({'labels': labels, 'codes': codes},
              open(os.path.join(OUT, 'segidx.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('files', len(files), 'labels', len(labels), 'codes', len(codes))
    # coverage check against rows
    rows = json.load(open(os.path.join(OUT, 'rows.json'), encoding='utf-8'))
    miss = [r['label'] for r in rows if r['label'] not in labels]
    print('rows', len(rows), 'labels missing from segidx', len(miss), miss[:5])

if __name__ == '__main__':
    main()
