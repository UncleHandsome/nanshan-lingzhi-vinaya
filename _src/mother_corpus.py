# -*- coding: utf-8 -*-
"""從《行事鈔資持記句級合編》docx 抽「記文→所釋鈔文」對照，測試與 _材料 的命中率。"""
import argparse
import glob
import io
import json
import os
import random
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOK = os.path.join(B, '_母本')
if not os.path.exists(os.path.join(BOOK, '_母本全序列.json')):
    BOOK = os.path.join(B, '測試', '重譯', '資持記')
DOCS = os.path.join(B, '白話', '行事鈔資持記句級合編_*.docx')
OUT = os.path.join(BOOK, '_母本對照.json')
OUT_SEQ = os.path.join(BOOK, '_母本全序列.json')


_VAR = str.maketrans('衆鉢爲説於着麤壍敎菓廻敍祕衞弃処体无証堕徳毗眞裏牀徧呪覩羣竝却',
                     '眾缽為說于著粗塹教果迴敘秘衛棄處體無證墮德毘真裡床遍咒睹群並卻')


def han(s):
    return re.sub(r'[^\u4e00-\u9fff]', '', s or '').translate(_VAR)


def read_docx():
    import docx
    pairs = []
    for p in sorted(glob.glob(DOCS)):
        last_chao = ''
        for para in docx.Document(p).paragraphs:
            t = para.text.strip()
            if t.startswith('【鈔】'):
                last_chao = t[3:].strip()
            elif t.startswith('【記】') and last_chao:
                pairs.append((han(t[3:]), han(last_chao)))
    return pairs


def read_docx_seq():
    """完整有序序列（保留鈔文標點與 docx 卷別），供 chao_for 取同卷前文。"""
    import docx
    seq = []
    for p in sorted(glob.glob(DOCS)):
        doc = os.path.basename(p)
        last_chao = ''
        for para in docx.Document(p).paragraphs:
            x = para.text.strip()
            if x.startswith('【鈔】'):
                last_chao = x[3:].strip()
            elif x.startswith('【記】') and last_chao:
                seq.append({'doc': doc, 'ji': han(x[3:]), 'chao': last_chao})
    return seq


def unit_of(path):
    t = io.open(path, encoding='utf-8', errors='ignore').read()
    m = re.search(r'【本次待審單元】(.*?)(?=【後文背景|【全書|\Z)', t, re.S)
    return han(m.group(1) if m else t)


_CACHE = None


def _pairs_json():
    """由 _母本對照.json 取 (記文, 所釋鈔文)；找不到檔就回空。"""
    global _CACHE
    if _CACHE is None:
        _CACHE = []
        if os.path.exists(OUT):
            d = json.load(io.open(OUT, encoding='utf-8'))
            for v in d.values():
                ji, chao = (v.get('ji') or '').strip(), (v.get('chao') or '').strip()
                if len(ji) >= 8 and chao:
                    _CACHE.append((ji, chao))
    return _CACHE


def _seq_json():
    if not os.path.exists(OUT_SEQ):
        return None
    try:
        return json.load(io.open(OUT_SEQ, encoding='utf-8'))
    except Exception:
        return None


def chao_for(unit_text):
    """依材料單元文字找所釋鈔文；優先用同卷完整序列，含前 1–2 段、總長 ≤800 字。"""
    u = han(unit_text)
    if len(u) < 8:
        return ''
    seq = _seq_json()
    if seq:
        tiers = (
            lambda ji: len(ji) >= 15 and ji in u,
            lambda ji: len(ji) >= 12 and (ji[:12] in u or ji[-12:] in u
                                          or (len(u) >= 12 and u in ji)),
            lambda ji: len(ji) >= 8 and (ji[:8] in u or ji[-8:] in u),
        )
        for ok in tiers:
            ms = [(len(x['ji']), k) for k, x in enumerate(seq) if ok(x['ji'])]
            if not ms:
                continue
            ms.sort(reverse=True)
            if ok is tiers[0] and ms and len(seq[ms[0][1]].get('ji') or '') >= 20:
                ms = ms[:1]
            out, seen, acc = [], set(), 0
            for _, k in ms[:2]:          # 最多取最長 2 筆，避免爆量
                grp = []
                # 由 k 往前收：先保核心母段，再補前 1–2 段背景
                for j in range(k, max(-1, k - 3), -1):
                    if seq[j].get('doc') != seq[k].get('doc'):
                        break
                    c = seq[j].get('chao') or ''
                    if c and c not in seen and not c.startswith('南山三大部之一'):
                        if (out or grp) and acc + len(c) + 1 > 800:
                            break
                        seen.add(c)
                        grp.insert(0, c)
                        acc += len(c) + 1
                out.extend(grp)
            txt = '\n'.join(out)
            return txt[:800]
    # 舊格式退路
    pairs = _pairs_json()
    tiers = (
        lambda ji: len(ji) >= 15 and ji in u,
        lambda ji: len(ji) >= 12 and (ji[:12] in u or ji[-12:] in u),
        lambda ji: len(ji) >= 8 and (ji[:8] in u or ji[-8:] in u),
        lambda ji: len(ji) >= 12 and any(ji[j:j + 8] in u for j in range(0, len(ji) - 7, 4)),
    )
    for ok in tiers:
        ms = [(len(ji), chao) for ji, chao in pairs if ok(ji)]
        if ms:
            ms.sort(reverse=True)
            seen = []
            for _, chao in ms[:2]:
                if chao and chao not in seen:
                    seen.append(chao)
            out = '\n'.join(seen)
            if out.startswith('南山三大部之一') or len(out) < 12:
                return ''
            return out[:800]
    return ''

def chao_for_units(texts, per=300):
    """打包組逐段取母本，避免只附到前 1–2 段。"""
    out = []
    for i, s in enumerate(texts, 1):
        c = chao_for(s)
        if c:
            out.append((('[%d] ' % i) if len(texts) > 1 else '') + c[:per])
    return '\n'.join(out)


def ji_for_chao(text, limit=6, cap=2200):
    """反向對照：給《行事鈔》文句，回傳所對應的《資持記》釋文。

    掃完所有 tier，收齊所有 ≥10 字命中，按原文順序；超 cap 時每條保留 70–100 字摘要，
    確保每個小點都露臉（不因先命中就 return，也不只取最長 8 條）。
    """
    u = han(text)
    if not u:
        return ''
    seq = _seq_json()
    if not seq:
        return ''
    tiers = (
        lambda ch: len(ch) >= 15 and ch in u,
        lambda ch: len(ch) >= 12 and (ch[:12] in u or ch[-12:] in u),
        lambda ch: len(ch) >= 10 and (ch[:10] in u or ch[-10:] in u),
        lambda ch: len(ch) >= 12 and any(ch[j:j + 8] in u
                                        for j in range(0, len(ch) - 7, 4)),
    )
    hit_idx = set()
    for ok in tiers:
        for i, x in enumerate(seq):
            ch = han(x.get('chao') or '')
            if ch and ok(ch):
                hit_idx.add(i)
    if not hit_idx:
        return ''
    segs, seen = [], set()
    for i in sorted(hit_idx):       # 原文順序，不按長度
        ji = (seq[i].get('ji') or '').strip()
        if ji and ji not in seen:
            seen.add(ji)
            segs.append(ji)
    if not segs:
        return ''
    total = sum(len(s) for s in segs) + len(segs) - 1
    if total <= cap:
        return '\n'.join(segs)
    # 每條保留 70–100 字摘要，所有小點都露臉
    per = max(70, min(100, (cap // max(1, len(segs))) - 1))
    outs = [s[:per] for s in segs]
    out = '\n'.join(outs)
    return out if len(out) <= cap + 200 else out[:cap + 200 - 1] + '…'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--test', type=int, default=20)
    ap.add_argument('--build', action='store_true')
    a = ap.parse_args()
    pairs = read_docx()
    print('docx pairs', len(pairs))
    mats = {}
    for f in os.listdir(os.path.join(BOOK, '_材料')):
        if f.endswith('.md'):
            mats[f[:-3]] = unit_of(os.path.join(BOOK, '_材料', f))
    print('materials', len(mats))
    # 以記文前 60 字建索引，命中後再確認包含關係
    idx = {}
    for ji, chao in pairs:
        if len(ji) >= 20:
            idx.setdefault(ji[:60], []).append((ji, chao))
    hit = 0
    mapping = {}
    sample = random.Random(20261119).sample(sorted(mats), min(a.test, len(mats)))
    for k in sample:
        u = mats[k]
        _ms = [(ji, chao) for ji, chao in pairs if len(ji) >= 15 and ji in u]
        found = None
        if _ms:
            _ms.sort(key=lambda x: -len(x[0]))
            found = _ms[0]
        if found:
            hit += 1
            mapping[k] = {'ji': found[0], 'chao': found[1]}
            print('HIT ', k, '記', len(found[0]), '鈔', len(found[1]))
        else:
            print('MISS', k, 'unit', len(u))
    print('hit %d / %d = %.0f%%' % (hit, len(sample), 100.0 * hit / max(1, len(sample))))
    if a.build:
        # 全量：只收 exact/包含且長度足夠者
        for k, u in mats.items():
            _ms = [(i, ji, chao) for i, (ji, chao) in enumerate(pairs) if len(ji) >= 15 and ji in u]
            if not _ms:
                _ms = [(i, ji, chao) for i, (ji, chao) in enumerate(pairs)
                       if len(ji) >= 12 and (ji[:12] in u or ji[-12:] in u)]
            if not _ms:
                _ms = [(i, ji, chao) for i, (ji, chao) in enumerate(pairs)
                       if len(ji) >= 8 and (ji[:8] in u or ji[-8:] in u)]
            if not _ms:
                _ms = [(i, ji, chao) for i, (ji, chao) in enumerate(pairs)
                       if len(ji) >= 12 and any(ji[j:j+8] in u for j in range(0, len(ji)-7, 4))]
            if _ms:
                _ms.sort(key=lambda x: x[0])
                _seen = set()
                _chao = []
                for _, ji, chao in _ms:
                    if chao and chao not in _seen:
                        _seen.add(chao)
                        _chao.append(chao)
                mapping[k] = {'ji': '\n'.join(x[1] for x in _ms), 'chao': '\n'.join(_chao), 'n': len(_ms)}
        io.open(OUT, 'w', encoding='utf-8').write(
            json.dumps(mapping, ensure_ascii=False, indent=1))
        print('wrote', OUT, len(mapping))
        seq = read_docx_seq()
        io.open(OUT_SEQ, 'w', encoding='utf-8').write(json.dumps(seq, ensure_ascii=False))
        print('wrote', OUT_SEQ, len(seq))


if __name__ == '__main__':
    main()
