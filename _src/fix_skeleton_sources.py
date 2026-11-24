# -*- coding: utf-8 -*-
"""修復 source 本身含 punctuation 骨架／空引號的段。"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fix_display_source as F

B = F.B
PUNCT_RUN = re.compile(r'[，。、；：？！「」『』《》〈〉（）〔〕【】…—·]{4,}')
EMPTY_PAIR = re.compile(r'(「」|《》|【】|『』|〈〉)')
RAWFILE = {'yeshu': r'TXT\03_四分律刪補隨機羯磨疏.txt'}
# 底本原字如此（二約位定人、二約法定用），不從句讀本改字；只補標點。
MANUAL = {
    ('07b_卷二之一_0016', 1): '五、明加結緣，正文二。初顯何人秉法，四位分之：二、約位定人，二、約法定用。',
}


def fill_brackets(src, rh, rs=None, re_=None):
    out = src
    for m in reversed(list(EMPTY_PAIR.finditer(src))):
        a, b = m.start(), m.end()
        pre = F.han(src[:a])[-12:]
        suf8 = F.han(src[b:])[:8]
        if len(pre) < 4 or len(suf8) < 3:
            return None
        lo = max(0, (rs or 0) - 200)
        hi = (re_ + 200) if re_ is not None else len(rh)
        p = rh.find(pre, lo, hi)
        if p < 0:
            p = rh.find(pre)
        if p < 0:
            return None
        p_end = p + len(pre)
        q = -1
        for L in (8, 6, 5, 4):
            q = rh.find(suf8[:L], p_end, p_end + 40)
            if q >= 0:
                break
        if q < 0:
            return None
        missing = rh[p_end:q]
        if not missing or len(missing) > 8:
            return None
        out = out[:a] + m.group(0)[0] + missing + m.group(0)[1] + out[b:]
    return out


def clean_anchors(src):
    runs = list(PUNCT_RUN.finditer(src))
    if not runs:
        return None, None
    return F.han(src[:runs[0].start()]), F.han(src[runs[-1].end():])


def main():
    apply = '--apply' in sys.argv
    book = 'yeshu'
    raw = io.open(os.path.join(B, RAWFILE[book]), encoding='utf-8').read()
    rh = F.han(raw)
    path = os.path.join(B, '定稿', book + '.jsonl')
    rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
    texts = {}
    ci = {}
    for name, txt in F.corpora(book):
        texts[name] = txt
        ci[name] = F.build_index(txt)
    changed = False
    for r in rows:
        rs, re_ = r.get('raw_start'), r.get('raw_end')
        segs = r.get('segments') or []
        for i, s in enumerate(segs):
            src = s.get('source') or ''
            if not (F.is_skeleton(src) or EMPTY_PAIR.search(src)):
                continue
            if (r['key'], i + 1) in MANUAL:
                disp = MANUAL[(r['key'], i + 1)]
                assert F.han(disp) in rh, r['key']
                print('OK', r['key'], i + 1, 'manual', repr(disp[:55]))
                if apply:
                    s['source'] = disp
                    s['display_source'] = disp
                    changed = True
                continue
            hs = F.han(src)
            disp = how = None
            # 1) 漢字完整：只是標點骨架 → 直接取語料句讀
            if rh.find(hs) >= 0:
                disp, how = F.resolve(hs, ci, texts)
                if disp:
                    how = 'han-intact/' + how
            # 2) 空引號補字
            if not disp and EMPTY_PAIR.search(src) and not PUNCT_RUN.search(src):
                filled = fill_brackets(src, rh, rs, re_)
                if filled and rh.find(F.han(filled)) >= 0:
                    disp, how = F.resolve(F.han(filled), ci, texts)
                    if not disp:
                        disp, how = filled, 'filled-only'
                    else:
                        how = 'fill/' + how
            # 3) 前後錨點還原
            if not disp:
                pre, suf = clean_anchors(src)
                if pre:
                    lo = max(0, (rs or 0) - 200)
                    hi = (re_ + 200) if re_ is not None else len(rh)
                    p = rh.find(pre, lo, hi)
                    if p < 0:
                        p = rh.find(pre)
                    if p >= 0:
                        end = p + len(pre)
                        if suf:
                            q = rh.find(suf, end, (re_ + 120) if re_ is not None else len(rh))
                            if q < 0:
                                q = rh.find(suf, end)
                            if q >= 0:
                                end = q + len(suf)
                        true_han = rh[p:end]
                        if re_ is not None and len(true_han) > (re_ - rs) * 1.5 + 20:
                            print('SPAN TOO BIG', r['key'], i + 1, len(true_han), 'region', re_ - rs)
                            continue
                        disp, how = F.resolve(true_han, ci, texts)
                        if disp:
                            how = 'anchor/' + how
            if not disp:
                print('FAIL', r['key'], i + 1, repr(src[:40]))
                continue
            print('OK', r['key'], i + 1, how, repr(disp[:55]))
            if apply:
                s['source'] = disp
                s['display_source'] = disp
                changed = True
    if apply and changed:
        for r in rows:
            src = r.get('source') or ''
            if F.is_skeleton(src) or EMPTY_PAIR.search(src):
                segs = r.get('segments') or []
                if segs:
                    r['source'] = '\n'.join(s.get('source') or '' for s in segs)
                    r['display_source'] = '\n'.join(s.get('display_source') or s.get('source') or '' for s in segs)
        io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
            json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
        print('saved')


if __name__ == '__main__':
    main()
