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

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

MAX_PRE_CHARS = 1800
MAX_POST_CHARS = 600
LONG_TAIL = ('\n（本項長文續段銜接優先於「語法自足／補全省略主賓」要求）'
            '本單元若切於句中未完處，須與前後片段自然銜接，勿重複補出已見前文的主詞，'
            '亦勿強加句號收尾；【前文背景】或【後文背景】中標為（本段前文）／（本段後文）之鄰接子句，'
            '僅供銜接語氣，嚴禁重複譯出')

BOOKS = {
    '業疏': dict(src='TXT_分卷_標點/03_業疏_標註', skip=0, nicao=False),
    '戒疏': dict(src='TXT_分卷/02_戒疏', skip=5, nicao=False),
    '尼鈔': dict(src='TXT_分卷/04_比丘尼鈔', skip=5, nicao=True),
    '行事鈔': dict(src='TXT_分卷/01_行事鈔', skip=5, nicao=True),
    '義鈔': dict(src='TXT_分卷/05_拾毗尼義鈔_標點對齊', skip=5, nicao=True),
    '資持記': dict(src='TXT_分卷/資持記_細分', skip=5, nicao=False, jionly=True),
}

SENT_END = '。！？；'
# 無標點底本（尼鈔／行事鈔）可用的句義邊界：句首虛字／連詞
SOFT_HEAD = ('若', '故', '此', '今', '又', '而', '則', '然', '但', '如', '所', '是', '其', '乃', '當', '應', '由', '從')


class UnsafeSplit(Exception):
    """找不到句義邊界，硬切會劈開字詞：保留缺口，不硬切。"""


def _best_cut(p, lo, hi):
    """在 [lo,hi) 內找最靠後的句義邊界；標點優先，其次句首虛字。找不到回 -1。"""
    lo = max(0, lo)
    hi = min(len(p), hi)
    if hi - lo < 2:
        return -1
    seg = p[lo:hi]
    for ch in ('。', '！', '？', '；', '，', '、', '：'):
        i = seg.rfind(ch)
        if i >= 0:
            return lo + i + 1
    for i in range(len(seg) - 1, 0, -1):
        if p[lo + i] in SOFT_HEAD:
            return lo + i
    return -1


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
            _cut = _best_cut(p, int(max_len * 0.5), int(max_len * 1.6))
            if _cut >= int(max_len * 0.4):
                out.append(p[:_cut])
                p = p[_cut:]
            else:
                # 找不到句義邊界：不可硬劈字詞
                raise UnsafeSplit('無句義邊界（餘 %d 字）' % len(p))
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
            _mid = _best_cut(text, int(max_len * 0.5), int(max_len * 1.6))
            if _mid < int(max_len * 0.4):
                raise UnsafeSplit('全段無句義邊界（%d 字）' % len(text))
            out = [text[:_mid], text[_mid:]]
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
    unsafe = []
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
            try:
                parts = split_sentences(body, args.max)
            except UnsafeSplit as e:
                print('  ⚠ 切點不安全（%s），保留缺口：%s 第 %d 段（%d 字）'
                      % (e, fn, idx + 1, len(body)))
                unsafe.append('%s\t第%d段\t%s\t%d字' % (chunk, idx + 1, e, len(body)))
                continue
            if len(parts) < 2:
                print('  ⚠ 長段未切開（max=%d，原文 %d 字），略過：%s 第 %d 段'
                      % (args.max, len(body), fn, idx + 1))
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
                _lab_full = lab + '文'
                _scope = _lab_full if args.book in ('業疏', '戒疏') else ('鈔文' if nicao else '記文')
                _bctx = _cfg.get('ctx', ('', ''))[0] if _lab_full in ('疏文', '記文') else ''
                if _lab_full == '疏文':
                    _sr = ''
                    _ban = _cfg.get('shuji_ban', '')
                elif _lab_full == '記文' and args.book in ('業疏', '戒疏'):
                    _sr = '記文釋義與科判動詞須與前文疏義相契，記中「疏云／鈔云／文云／注云」依所釋之書判讀；'
                    _ban = ''
                else:
                    _sr = _cfg.get('ctx', ('', ''))[1] if _lab_full in ('疏文', '記文') else ''
                    _ban = _cfg.get('shuji_ban', '') if _lab_full == '疏文' else ''
                if _lab_full not in ('疏文', '記文'):
                    _bctx = _sr = _ban = ''
                if (not _bctx and _cfg.get('note') and (args.book not in ('業疏', '戒疏') or _lab_full in ('疏文', '記文'))):
                    _bctx = _cfg['note']
                prompt = BLIND_PROMPT.format(
                    scope=_scope, book_ctx=_bctx, shuji_rule=_sr, shuji_ban=_ban,
                    tail_rule=LONG_TAIL, logic_checklist=BC.LOGIC_CHECKLIST, style_spec=BC.STYLE_SPEC, out_format=fmt)
                _pn = "\n\n（本單元為長文第 %d/%d 部分，只譯這一部分，勿補前後文。）" % (pi, len(parts))
                _j = prompt.find("照下列完整標籤輸出")
                prompt = (prompt[:_j] + _pn + "\n" + prompt[_j:]) if _j >= 0 else (prompt + _pn)
                L = [prompt, '', '---', '',
                     '（出處：《%s》%s，第 %d 段之 %d/%d）' % (args.book, chunk, idx + 1, pi, len(parts)), '']
                if pre:
                    L += ['【前文背景（僅供參考，嚴禁譯入正文）】', ''] + pre + ['']
                L += ['【本次待譯單元】', '', '■ %s文（原文）' % lab, '', seg, '']
                if post_lines or post_seg:
                    L += ['【後文背景（僅供參考，嚴禁譯入正文）】', ''] + post_seg + post_lines + ['']
                if args.book == '資持記':
                    try:
                        import mother_corpus as MC
                        _mch = MC.chao_for(seg) or MC.chao_for(body)
                        if _mch:
                            L += ['【所釋鈔文（僅供對照，嚴禁譯入正文）】', '', _mch, '']
                    except Exception:
                        pass

                n += 1
                name = '%s_%04d_%02d.md' % (chunk, idx, pi)
                io.open(os.path.join(out, '_材料', name), 'w', encoding='utf-8').write('\n'.join(L))
                io.open(os.path.join(out, '_盲翻', name), 'w', encoding='utf-8').write('\n'.join(L))
                mapping.append({'file': name, 'chunk': chunk, 'idx': idx, 'part': pi,
                                'total': len(parts)})

    json.dump(mapping, io.open(os.path.join(out, '_對應.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    if unsafe:
        io.open(os.path.join(out, '_切點不安全.log'), 'w', encoding='utf-8').write('\n'.join(unsafe) + '\n')
    print('%s：長段切出 %d 小段（含前 %d 後 %d 背景）→ 測試/重譯/%s/_長段'
          % (args.book, n, args.front, args.back, args.book))
    if unsafe:
        print('  切點不安全 %d 段（已保留缺口，見 _切點不安全.log）' % len(unsafe))


if __name__ == '__main__':
    main()
