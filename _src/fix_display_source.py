# -*- coding: utf-8 -*-
"""修復 display_source 漢字序列與 source 不一致的列／段。

做法：在句讀語料中唯一搜尋 source 的漢字序列，取對應含標點片段重建 display_source。
不改 source、translation、segments 結構。
"""
import argparse
import glob
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HAN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\uf900-\ufaff]')
BOOKS = ['xingshichao', 'jieshu', 'yeshu', 'nicao', 'yichao', 'zhichi']
CORPUS_DIRS = {
    'xingshichao': [r'TXT_分卷\01_行事鈔'],
    'jieshu': [r'TXT_分卷\02_戒疏'],
    'yeshu': [r'TXT_分卷_標點\03_業疏', r'TXT_句讀\03_業疏'],
    'nicao': [r'TXT_分卷\04_比丘尼鈔', r'TXT_句讀\04_尼鈔'],
    'yichao': [r'TXT_分卷\05_拾毗尼義鈔_標點', r'TXT_分卷\05_拾毗尼義鈔'],
    'zhichi': [r'TXT_分卷\資持記'],
}


def han(s):
    return ''.join(HAN.findall(s or ''))


LABEL_RE = re.compile(r'【(?:疏|記|鈔|律|註|序)(?:文|序)?】')
WS_RE = re.compile(r'\s')


NONCJK_RE = re.compile(r'[\sA-Za-z0-9\uFF10-\uFF19]+')
CJK_PUNCT = '，。、；：？！「」『』《》〈〉（）〔〕【】…—·〜～﹑﹔'


def density(s):
    nw = NONCJK_RE.sub('', s or '')
    if not nw:
        return 1.0
    return len(han(s)) / len(nw)


EMPTY_BRACKET = re.compile(r'【】|《》|「」|『』|〈〉')


PUNCT_RUN4 = re.compile(r'[，。、；：？！「」『』《》〈〉（）〔〕【】…—·]{4,}')


def is_skeleton(s):
    s = s or ''
    if EMPTY_BRACKET.search(s):
        return True
    nw = NONCJK_RE.sub('', s)
    if len(nw) > 20 and density(s) < 0.4:
        return True
    if PUNCT_RUN4.search(s) and density(s) < 0.5:
        return True
    return False


def build_index(text):
    text = LABEL_RE.sub('', text)
    chars = []
    idx = []
    for i, ch in enumerate(text):
        if HAN.match(ch):
            chars.append(ch)
            idx.append(i)
    return ''.join(chars), idx


def corpora(book):
    out = []
    p = os.path.join(B, 'TXT_句讀校定', book + '.txt')
    if os.path.exists(p):
        out.append((p, LABEL_RE.sub('', io.open(p, encoding='utf-8').read())))
    for d in CORPUS_DIRS.get(book, []):
        files = sorted(glob.glob(os.path.join(B, d, '*.txt')))
        if files:
            txt = '\n'.join(io.open(f, encoding='utf-8').read() for f in files)
            out.append((d, LABEL_RE.sub('', txt)))
    return out


def locate(target, corp_index, texts):
    """依語料順序找第一個「唯一命中且非骨架」的語料；回傳 [(name, pos)] 或 []。"""
    for name, (h, idx) in corp_index.items():
        k = h.find(target)
        if k < 0:
            continue
        if h.find(target, k + 1) >= 0:
            continue  # 此語料內不唯一，換下一個
        if is_skeleton(rebuild(target, corp_index, name, k, texts)):
            continue  # 命中區本身是 punctuation 骨架，換下一個
        return [(name, k)]
    return []


def rebuild(target, corp_index, name, pos, texts):
    h, idx = corp_index[name]
    a = idx[pos]
    last = pos + len(target) - 1
    b = idx[last] + 1
    # 含句末標點：延伸到下一個漢字之前
    if last + 1 < len(idx):
        b = idx[last + 1]
    else:
        b = len(texts[name])
    disp = texts[name][a:b].strip()
    assert han(disp) == target
    return disp


def split_rebuild(target, corp_index, texts):
    """source 由不相鄰片段合併而成： greedy 切成正序唯一命中的片段再重建。"""
    parts = []
    rest = target
    last_pos = -1
    last_name = None
    while rest:
        found = None
        for L in range(len(rest), 3, -1):
            hits = locate(rest[:L], corp_index, texts)
            if hits:
                name, pos = hits[0]
                if last_name is not None and name == last_name and pos <= last_pos:
                    continue
                found = (name, pos, L)
                break
        if not found:
            return None
        name, pos, L = found
        parts.append(rebuild(rest[:L], corp_index, name, pos, texts))
        last_name, last_pos = name, pos + L - 1
        rest = rest[L:]
    disp = '\n'.join(parts)
    if han(disp) == target:
        return disp
    return None


def align_rebuild(target, corp_index, texts):
    """底本用字與語料不同：以 longest-prefix 錨點＋序列比對轉移標點。"""
    import difflib
    best = (0, None, None)
    for name, (h, idx) in corp_index.items():
        txt = texts[name]
        for L in range(len(target), 4, -1):
            p = h.find(target[:L])
            if p >= 0:
                end_han = min(len(h), p + len(target) + 12)
                tend = idx[end_han] if end_han < len(h) else len(txt)
                w = txt[idx[p]:tend]
                if not is_skeleton(w) and L > best[0]:
                    best = (L, name, p)
                break
    L, name, pos = best
    if name is None:
        return None
    h, idx = corp_index[name]
    txt = texts[name]
    end_han = min(len(h), pos + len(target) + 12)
    tend = idx[end_han] if end_han < len(h) else len(txt)
    window = txt[idx[pos]:tend]
    if is_skeleton(window):
        return None
    widx = [i for i, ch in enumerate(window) if HAN.match(ch)]
    wh = ''.join(window[i] for i in widx)
    sm = difflib.SequenceMatcher(None, target, wh, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            a = widx[j1]
            b = widx[j2] if j2 < len(widx) else len(window)
            out.append(window[a:b])
        elif tag in ('replace', 'delete'):
            out.append(target[i1:i2])
        # insert：語料多出的字（底本無）→ 跳過
    disp = ''.join(out).strip()
    if han(disp) == target:
        return disp
    return None


def tidy(d):
    d = EMPTY_BRACKET.sub('', d)
    d = re.sub(r'[【】]', '', d)
    d = re.sub(r'「(?=[下，。、；：])', '', d)
    d = d.replace('\n\n', '\x00').replace('\n', '').replace('\x00', '\n')
    return d.strip()


def bad_result(d):
    return is_skeleton(d) or (PUNCT_RUN4.search(d) and density(d) < 0.65)


def resolve(target, corp_index, texts):
    hits = locate(target, corp_index, texts)
    if hits:
        name, pos = hits[0]
        d = rebuild(target, corp_index, name, pos, texts)
        if not bad_result(d):
            return d, 'unique'
    d = split_rebuild(target, corp_index, texts)
    if d and not bad_result(d):
        return tidy(d), 'split'
    d = align_rebuild(target, corp_index, texts)
    if d and not bad_result(d):
        return tidy(d), 'align'
    return None, 'fail'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    report = {}
    for book in BOOKS:
        path = os.path.join(B, '定稿', book + '.jsonl')
        rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
        texts = {}
        corp_index = {}
        for name, txt in corpora(book):
            texts[name] = txt
            corp_index[name] = build_index(txt)
        fixed_row = fixed_seg = 0
        unresolved = []
        changed = False
        for r in rows:
            hs = han(r.get('source'))
            d = r.get('display_source') or ''
            if d.strip() and (han(d) != hs or is_skeleton(d)):
                nd, how = resolve(hs, corp_index, texts)
                if nd:
                    r['display_source'] = nd
                    fixed_row += 1
                    changed = True
                else:
                    unresolved.append(('row', r['key'], how))
            for i, s in enumerate(r.get('segments') or []):
                ss = han(s.get('source'))
                sd = s.get('display_source') or ''
                if sd.strip() and (han(sd) != ss or is_skeleton(sd)):
                    nd, how = resolve(ss, corp_index, texts)
                    if nd:
                        s['display_source'] = nd
                        fixed_seg += 1
                        changed = True
                    else:
                        unresolved.append(('seg', r['key'], i + 1, how))
        report[book] = {'fixed_row': fixed_row, 'fixed_seg': fixed_seg,
                        'unresolved': unresolved}
        print(book, 'fixed_row', fixed_row, 'fixed_seg', fixed_seg,
              'unresolved', len(unresolved), flush=True)
        for u in unresolved[:10]:
            print('  ', u, flush=True)
        if a.apply and changed:
            shutil.copy2(path, os.path.join(B, '定稿', '_舊_%s_before_dispfix_20261124.jsonl' % book))
            io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
                json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
    io.open(os.path.join(B, '重作材料_長段', 'display_fix_report_20261124.json'), 'w',
            encoding='utf-8').write(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
