# -*- coding: utf-8 -*-
"""把六書 500 字 Qwen 回覆套回 定稿/*.jsonl。"""
import glob
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '重作材料_長段', 'Qwen500_輸出_v1_20261124')
BOOKS = [
    ('01_行事鈔', 'xingshichao'),
    ('02_戒本疏行宗記', 'jieshu'),
    ('03_業疏', 'yeshu'),
    ('04_尼鈔', 'nicao'),
    ('05_義鈔', 'yichao'),
    ('06_資持記', 'zhichi'),
]

# 明確還原：Qwen 過度縮短，不再套用
REVERT = {
    ('xingshichao', 'GAP52'), ('xingshichao', 'GAP26'), ('xingshichao', '282'),
    ('yichao', '28'), ('nicao', '267'),
    ('jieshu', '05b_卷二上之一_0116'), ('jieshu', '18b_卷四上之三_0019'),
    ('jieshu', '08b_卷二下之一_0075'), ('jieshu', '11b_卷三上之二_0150'),
}
HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return len(HAN.findall(s or ''))


def load_jsonl(path):
    return [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]


def dump_jsonl(path, rows):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def split_by_labels(text, segs):
    """若 Qwen 回覆保留【疏文】【記文】標籤，依標籤精確切回 segments。"""
    labs = [(s.get('label') or '疏文').strip() for s in segs]
    pat = re.compile(r'【(疏文|記文|鈔文|律文|註文|序文)】')
    ms = list(pat.finditer(text))
    if len(ms) != len(segs):
        return None
    if [m.group(1) for m in ms] != labs:
        return None
    parts = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        part = text[m.end():end].strip()
        if i == 0 and text[:m.start()].strip():
            part = text[:m.start()].strip() + '\n\n' + part
        if not part:
            return None
        parts.append(part)
    return parts


def split_by_weights(text, segs):
    """把整段譯文依原 segment 長度比例切成 n 段；切不開回傳 None。"""
    n = len(segs)
    if n <= 1:
        return [text]
    blocks = [x.strip() for x in re.split(r'\n\s*\n', text.strip()) if x.strip()]
    if len(blocks) < n:
        blocks = [x.strip() for x in re.split(r'(?<=[。！？])', text.strip()) if x.strip()]
    if len(blocks) < n:
        return None
    weights = [max(1, len((s.get('translation') or s.get('source') or ''))) for s in segs]
    total = sum(weights)
    # 先依比例分配 block 數，每個至少 1
    raw = [max(1, round(len(blocks) * w / total)) for w in weights]
    while sum(raw) > len(blocks):
        i = max(range(n), key=lambda j: raw[j] if raw[j] > 1 else -1)
        raw[i] -= 1
    while sum(raw) < len(blocks):
        i = max(range(n), key=lambda j: weights[j] / raw[j])
        raw[i] += 1
    out = []
    pos = 0
    for cnt in raw:
        out.append('\n\n'.join(blocks[pos:pos + cnt]))
        pos += cnt
    return out


def combine_segments(segs, text):
    src = ''.join((s.get('source') or '') for s in segs)
    disp = ''.join((s.get('display_source') or s.get('source') or '') for s in segs)
    first = dict(segs[0])
    first['source'] = src
    first['display_source'] = disp
    first['translation'] = text
    return [first]


def apply(book_folder, book_id, dry=False):
    path = os.path.join(B, '定稿', book_id + '.jsonl')
    backup = os.path.join(B, '定稿', '_舊_' + book_id + '_before_qwen500_20261124.jsonl')
    rows = load_jsonl(backup)
    base = {str(r['key']): r for r in rows}
    replies = {}
    for p in glob.glob(os.path.join(ROOT, book_folder) + r'\*_修正.jsonl'):
        for ln in io.open(p, encoding='utf-8'):
            ln = ln.strip()
            if not ln:
                continue
            o = json.loads(ln)
            k = str(o.get('key', ''))
            if '／' in k:
                k = k.rsplit('／', 1)[-1]
            elif '/' in k:
                k = k.rsplit('/', 1)[-1]
            replies[k] = (p, o)
    changed = single = split = combined = skipped = 0
    skip_keys = []
    for k, (p, o) in replies.items():
        r = base.get(k)
        if (book_id, k) in REVERT:
            skipped += 1
            skip_keys.append((k, 'reverted'))
            continue
        if not r:
            skipped += 1
            skip_keys.append((k, os.path.basename(p)))
            continue
        tr = str(o.get('translation') or '').strip()
        if not tr:
            skipped += 1
            skip_keys.append((k, os.path.basename(p) + ':empty'))
            continue
        old = r.get('translation', '')
        segs = r.get('segments') or []
        new_segs = None
        if len(segs) > 1:
            parts = split_by_labels(tr, segs)
            if parts:
                new_segs = []
                for s, part in zip(segs, parts):
                    s2 = dict(s)
                    s2['translation'] = part
                    new_segs.append(s2)
                split += 1
            else:
                skipped += 1
                skip_keys.append((k, 'no segment labels'))
                continue
        elif segs:
            s2 = dict(segs[0])
            s2['translation'] = tr
            new_segs = [s2]
            single += 1
        else:
            single += 1
        r['translation'] = tr
        if new_segs is not None:
            r['segments'] = new_segs
        changed += 1
    if not dry:
        dump_jsonl(path, rows)
    print(book_id, 'rows', len(rows), 'replies', len(replies), 'changed', changed,
          'single', single, 'split', split, 'combined', combined,
          'skipped', skipped, 'skip_keys', skip_keys)


def main():
    for folder, bid in BOOKS:
        apply(folder, bid)


if __name__ == '__main__':
    main()
