# -*- coding: utf-8 -*-
"""把使用者自己跑出來的回覆（含 JSONL 區塊的 .txt）匯入批次輸出目錄。

重點：
1. key 在不同書之間會重複 → 用「書名＋key」定位（取該 key 在文中最近出現的書名）
2. GAP44-5 這種 key 的「-5」是 key 的一部分，不能亂剝
   → 先比完整 key，找不到才逐段剝尾碼（給 _0006-1 這種分段 key 用）
3. 寫 <stem>_回.txt（已存在就不覆蓋）＋ fixes.jsonl
"""
import glob
import io
import json
import os
import difflib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_3k_review as R
import book_prompt

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '六書_3K_20261124')
RUN = os.path.join(B, '六書_3K_跑_20261124')
RAW = os.path.join(RUN, '輸出')
BLOCK = os.path.join(B, '審查擋檔_20261125')
FIXES = os.path.join(RUN, 'fixes.jsonl')

HEAD_RE = re.compile(r'^##\s+([^／\n]+)／(.+?)\s*$', re.M)
LABELS = {v['name']: k for k, v in book_prompt.PROFILES.items()}
LABELS.update({'行事鈔': 'xingshichao', '戒疏': 'jieshu', '戒本疏': 'jieshu',
               '業疏': 'yeshu', '尼鈔': 'nicao', '義鈔': 'yichao', '資持記': 'zhichi'})
NAME_ALT = '|'.join(sorted((re.escape(k) for k in LABELS), key=len, reverse=True))


def clip(x):
    return str(x or '').strip().strip('[]「」')


def build_index():
    """exact[(book, key)] = stem；keys_of[stem] = [key,...]"""
    exact = {}
    keys_of = {}
    any_book = {}
    for p in glob.glob(os.path.join(MAT, '*.md')):
        stem = os.path.basename(p)[:-3]
        book = stem.rsplit('_', 1)[-1]
        ks = [m.group(2).strip() for m in HEAD_RE.finditer(io.open(p, encoding='utf-8').read())]
        keys_of[stem] = ks
        for k in ks:
            exact[(book, k)] = stem
            any_book.setdefault(k, set()).add(book)
    return exact, keys_of, any_book


def current_stems():
    """本輪審查的檔案（審查擋檔資料夾裡的 .md）。"""
    return {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(BLOCK, '*.md'))}


def resolve(exact, book, key, any_book=None, current=None):
    """先完整 key，再逐段剝尾碼；再退而用「全書唯一 key」。回傳 (stem, 實際 key, 書別)。"""
    key = clip(key)
    current = current or set()
    # 0) 本輪檔案裡若只有一個檔含此 key，直接採用
    if current:
        hits = [s for (b, k), s in exact.items() if k == key and s in current]
        if len(set(hits)) == 1:
            s = hits[0]
            return s, key, s.rsplit('_', 1)[-1]
    if book and (book, key) in exact:
        return exact[(book, key)], key, book
    kk = key
    while '-' in kk:
        kk = kk.rsplit('-', 1)[0]
        if book and (book, kk) in exact:
            return exact[(book, kk)], kk, book
    if any_book:
        books = any_book.get(key) or any_book.get(kk) or set()
        if len(books) == 1:
            b2 = next(iter(books))
            k2 = key if (b2, key) in exact else kk
            if (b2, k2) in exact:
                return exact[(b2, k2)], k2, b2
    return None, key, book


def _norm(s):
    return re.sub(r'[\s【】〔〕（）()「」『』，。！？、；：…]', '', s or '')


def pick_by_text(exact, km, any_book, key, tr, fallback_book=None):
    """key 在多本書都有時，用譯文跟各檔現有譯文比對，取最相似者。"""
    books = any_book.get(key) or set()
    if fallback_book:
        books = books | {fallback_book}
    best = None
    a1 = _norm(tr)
    for b in books:
        stem = exact.get((b, key))
        if not stem:
            continue
        ent = km.get('%s|%s' % (b, key))
        cur = _norm(ent[4].get('translation') if ent else '')
        if len(cur) < 20 or len(a1) < 20:
            continue
        r = difflib.SequenceMatcher(None, a1, cur).quick_ratio()
        if best is None or r > best[0]:
            best = (r, stem, key, b)
    if best and best[0] >= 0.5:
        return best[1], best[2], best[3]
    return None, key, fallback_book


def _occurrences(text):
    lines = text.split('\n')
    occ = []
    marks = []
    for i, ln in enumerate(lines):
        for m in re.finditer(r'(%s)[*_ ]*／[*_ ]*([^\s\n]+)' % NAME_ALT, ln):
            lab = m.group(1)
            if lab not in LABELS:
                continue
            book = LABELS[lab]
            marks.append((i, book))
            tail = re.split(r'[*：:。，,；;（(「」]', m.group(2))[0]
            for tok in tail.split('、'):
                tok = tok.strip().strip('*_`')
                if not tok:
                    continue
                mr = re.match(r'^(\d+)\s*[～~]\s*(\d+)$', tok)
                if mr and 0 < int(mr.group(2)) - int(mr.group(1)) <= 200:
                    occ += [(i, str(n), book) for n in range(int(mr.group(1)), int(mr.group(2)) + 1)]
                else:
                    occ.append((i, tok, book))
    return occ, marks


def extract_objs(text):
    occ, marks = _occurrences(text)
    lines = text.split('\n')
    out = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith('```') or not s.startswith('{'):
            continue
        try:
            o = json.loads(s)
        except Exception:
            continue
        if not isinstance(o, dict) or 'key' not in o:
            continue
        k = clip(o.get('key'))
        cand = [x for x in occ if x[1] == k]
        if cand:
            book = min(cand, key=lambda x: abs(x[0] - i))[2]
        else:
            before = [x for x in marks if x[0] <= i]
            after = [x for x in marks if x[0] > i]
            book = (before[-1][1] if before else (after[0][1] if after else None))
        out.append((s, o, book))
    return out


def main():
    args = [a for a in sys.argv[1:] if a != '--dry']
    dry = '--dry' in sys.argv
    if not args:
        print('usage: ingest_user_reply.py [--dry] <file.txt> ...')
        return
    exact, keys_of, any_book = build_index()
    current = current_stems()
    if current:
        print('本輪檔案 %d 個（優先以此為候選）' % len(current))
    km = R.all_segment_keys()
    print('材料 key 總數', len(exact))

    per_stem = {}
    unmatched = []
    for f in args:
        text = io.open(f, encoding='utf-8').read()
        objs = extract_objs(text)
        print('%s：%d 個 JSON' % (os.path.basename(f), len(objs)))
        resolved = []
        for idx, (line, o, book) in enumerate(objs):
            stem, mk, bk = resolve(exact, book, o.get('key'), any_book, current)
            resolved.append((idx, line, o, stem, mk, bk))
        # 第二輪：沒對上的，用鄰近已對上物件的書別多數決
        for idx, line, o, stem, mk, bk in resolved:
            if stem:
                per_stem.setdefault(stem, []).append((mk, line, o))
                continue
            if not stem:
                st3, mk3, bk3 = pick_by_text(exact, km, any_book,
                                             clip(o.get('key')), o.get('translation') or '', bk)
                if st3:
                    stem, mk = st3, mk3
            votes = {}
            for j2, _, _, s2, _, b2 in resolved:
                if s2 and abs(j2 - idx) <= 30 and b2:
                    votes[b2] = votes.get(b2, 0) + 1
            if not stem and votes:
                b3 = max(votes, key=lambda x: votes[x])
                stem2, mk2, _ = resolve(exact, b3, o.get('key'), None, current)
                if stem2:
                    stem, mk = stem2, mk2
            if not stem:
                unmatched.append('%s/%s' % (bk, o.get('key')))
                continue
            per_stem.setdefault(stem, []).append((mk, line, o))
            resolved[idx] = (idx, line, o, stem, mk, bk)

    print('對應 %d 個材料檔，未對應 %d%s' % (
        len(per_stem), len(unmatched), ('：' + ','.join(unmatched[:8])) if unmatched else ''))
    if dry:
        for stem, items in sorted(per_stem.items()):
            print('  %-24s %2d key' % (stem, len(items)))
        return

    os.makedirs(RAW, exist_ok=True)
    n_reply = n_fix = n_skip = 0
    fix_lines = []
    for stem, items in sorted(per_stem.items()):
        dst = os.path.join(RAW, stem + '_回.txt')
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            n_skip += 1
            continue
        io.open(dst, 'w', encoding='utf-8', newline='\n').write(
            '\n'.join(line for _, line, _ in items) + '\n')
        n_reply += 1
        book = stem.rsplit('_', 1)[-1]
        for mk, _, o in items:
            if str(o.get('status', '')).lower() == 'fixed' and (o.get('translation') or '').strip():
                fix_lines.append(json.dumps({'book': book, 'mk': mk,
                                             'translation': o['translation']}, ensure_ascii=False))
                n_fix += 1
    if fix_lines:
        with io.open(FIXES, 'a', encoding='utf-8', newline='\n') as fh:
            fh.write('\n'.join(fix_lines) + '\n')
    print('寫入回覆 %d（已存在跳過 %d），追加 fixes %d' % (n_reply, n_skip, n_fix))


if __name__ == '__main__':
    main()
