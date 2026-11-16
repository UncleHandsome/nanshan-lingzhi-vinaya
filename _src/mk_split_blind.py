# -*- coding: utf-8 -*-
"""超長段落按句切段（含前後文背景），產生盲翻材料與對應表。

用法：
  python -X utf8 _src/mk_split_blind.py --book 行事鈔 --max 400 --front 6 --back 4
"""
import argparse
import io
import json
import os
import re
import book_config as BC

MAX_PRE_CHARS = 900
MAX_POST_CHARS = 600
LONG_TAIL = ('本單元若切於句中未完處，須與前後片段自然銜接，勿重複補出已見前文的主詞，亦勿強加句號收尾；【前文背景】或【後文背景】中標為（本段前文）／（本段後文）之鄰接子句，僅供銜接語氣，嚴禁重複譯出')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

BOOKS = {
    '業疏': dict(src='TXT_分卷_標點/03_業疏_標註', skip=0, nicao=False),
    '戒疏': dict(src='TXT_分卷/02_戒疏', skip=5, nicao=False),
    '尼鈔': dict(src='TXT_分卷/04_比丘尼鈔', skip=5, nicao=True),
    '行事鈔': dict(src='TXT_分卷/01_行事鈔', skip=5, nicao=True),
    '義鈔': dict(src='TXT_分卷/05_拾毗尼義鈔_標點對齊', skip=5, nicao=True),
    '資持記': dict(src='TXT_分卷/資持記_細分', skip=5, nicao=False, jionly=True),
}

SENT_END = '。！？；'

from mk_blind_materials import BLIND_PROMPT  # 共用同一份盲翻模板


def split_sentences(text, max_len):
    parts, buf = [], ''
    _depth = 0
    for ch in text:
        buf += ch
        if ch in '「『':
            _depth += 1
        elif ch in '」』':
            _depth = max(0, _depth - 1)
        if ch in SENT_END and _depth == 0 and len(buf) >= max_len * 0.6:
            parts.append(buf)
            buf = ''
    if buf:
        if parts and len(buf) < max_len * 0.3:
            parts[-1] += buf
        else:
            parts.append(buf)
    out = []
    for p in parts:
        while len(p) > max_len * 1.8:
            _cut = max(p.rfind('，', 0, max_len), p.rfind('、', 0, max_len),
                       p.rfind('；', 0, max_len), p.rfind('。', 0, max_len),
                       p.rfind('！', 0, max_len), p.rfind('？', 0, max_len))
            if _cut >= int(max_len * 0.6):
                out.append(p[:_cut + 1])
                p = p[_cut + 1:]
            else:
                out.append(p[:max_len])
                p = p[max_len:]
        if p:
            out.append(p)
    # 進得來（原文已 > min）就必須至少兩段，否則下游會整段漏掉
    if len(out) < 2 and len(text) > max_len:
        chunks = [c for c in re.split(r'(?<=[，、；])', text) if c]
        if len(chunks) >= 2:
            half, acc, out2 = len(text) // 2, 0, []
            for c in chunks:
                acc += len(c)
                out2.append(c)
                if acc >= half and len(out2) < len(chunks):
                    break
            out = [''.join(out2), ''.join(chunks[len(out2):])]
        else:
            mid = len(text) // 2
            _q = text.rfind('，', 0, mid)
            if _q > mid * 0.6:
                mid = _q + 1
            out = [text[:mid], text[mid:]]
    return [x for x in out if x]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True)
    ap.add_argument('--max', type=int, default=400)
    ap.add_argument('--min', type=int, default=500, help='超過此長度才切')
    ap.add_argument('--front', type=int, default=6)
    ap.add_argument('--back', type=int, default=4)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    spec = BOOKS[args.book]
    sd = os.path.join(B, spec['src'].replace('/', os.sep))
    out = os.path.join(B, '測試', '重譯', args.book, '_長段')
    _bd = os.path.join(out, '_盲翻')
    if os.path.isdir(_bd) and os.listdir(_bd) and not args.force:
        raise SystemExit('長段輸出已存在，請先移走或加 --force：' + _bd)
    for sub in ('_材料', '_盲翻'):
        d = os.path.join(out, sub)
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if os.path.isfile(fp):
                os.remove(fp)

    nicao = spec['nicao']
    jionly = spec.get('jionly', False)

    mapping = []
    n = 0
    for fn in sorted(os.listdir(sd)):
        if not fn.endswith('.txt'):
            continue
        chunk = fn[:-4]
        lines = [x.strip() for x in io.open(os.path.join(sd, fn), encoding='utf-8', errors='ignore')
                 .read().split('\n')[spec['skip']:] if x.strip()]
        for idx, line in enumerate(lines):
            if len(line) <= args.min:
                continue
            body = re.sub(r'^【(.)】\s*', '', line)
            lab = re.match(r'^【(.)】', line)
            lab = lab.group(1) if lab else ('記' if jionly else ('鈔' if nicao else '疏'))
            fmt = '【%s文】……' % lab
            parts = split_sentences(body, args.max)
            if len(parts) < 2:
                continue
            pre_lines = []
            _acc = 0
            for k in range(idx - 1, max(-1, idx - args.front - 1), -1):
                _ln = lines[k]
                if _acc + len(_ln) > MAX_PRE_CHARS and pre_lines:
                    break
                pre_lines.insert(0, _ln)
                _acc += len(_ln)
            post_lines = []
            _acc = 0
            for k in range(idx + 1, min(len(lines), idx + 1 + args.back)):
                _ln = lines[k]
                if _acc + len(_ln) > MAX_POST_CHARS and post_lines:
                    break
                post_lines.append(_ln)
                _acc += len(_ln)

            for pi, seg in enumerate(parts, 1):
                pre = list(pre_lines)
                if pi > 1:
                    pre = pre + ['【%s】（本段前文）%s' % (lab, parts[pi - 2][-260:])]
                post_seg = []
                if pi < len(parts):
                    post_seg = ['【%s】（本段後文）%s' % (lab, parts[pi][:260])]
                _cfg = BC.cfg(args.book)
                _bctx = _cfg.get('ctx', ('', ''))[0]
                if _cfg.get('note') and not _bctx:
                    _bctx = _cfg['note']
                prompt = BLIND_PROMPT.format(
                    scope=('鈔文' if nicao else ('記文' if jionly else '疏文與記文')),
                    book_ctx=_bctx,
                    shuji_rule=_cfg.get('ctx', ('', ''))[1],
                    shuji_ban=_cfg.get('shuji_ban', ''),
                    tail_rule=LONG_TAIL, out_format=fmt)
                prompt += '\n\n（本單元為長文第 %d/%d 部分，只譯這一部分，勿補前後文。）' % (pi, len(parts))
                L = [prompt, '', '---', '',
                     '（出處：%s，第 %d 段之 %d/%d）' % (chunk, idx + 1, pi, len(parts)), '']
                if pre:
                    L += ['【前文背景（僅供參考，嚴禁譯入正文）】', ''] + pre + ['']
                L += ['【本次待譯單元】', '', '■ %s文（原文）' % lab, '', seg, '']
                if post_lines or post_seg:
                    L += ['【後文背景（僅供參考，嚴禁譯入正文）】', ''] + post_seg + post_lines + ['']

                n += 1
                name = '%s_%04d_%02d.md' % (chunk, idx, pi)
                io.open(os.path.join(out, '_材料', name), 'w', encoding='utf-8').write('\n'.join(L))
                io.open(os.path.join(out, '_盲翻', name), 'w', encoding='utf-8').write('\n'.join(L))
                mapping.append({'file': name, 'chunk': chunk, 'idx': idx, 'part': pi,
                                'total': len(parts)})

    json.dump(mapping, io.open(os.path.join(out, '_對應.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('%s：長段切出 %d 小段（含前 %d 後 %d 背景）→ 測試/重譯/%s/_長段'
          % (args.book, n, args.front, args.back, args.book))


if __name__ == '__main__':
    main()
