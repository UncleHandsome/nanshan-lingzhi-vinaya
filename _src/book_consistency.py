# -*- coding: utf-8 -*-
"""全書一致性掃描（book_consistency）：只報告，不改任何資料。

規格（reaudit.txt 第 3/3 篇 §三）：
  1. 典籍稱謂統計與對齊（四分律／母論／婆論／婆沙論／多論／見論／雜含／智論／善生／
     五百問事／隨機羯磨；並抓《毘尼母論》／《毘尼母經》、《善見論》／《善見律毘婆沙》混用）。
  2. 高頻專詞雙軌（波羅夷 vs 斷頭重罪、形俱戒 vs 盡形壽戒、破內外道 vs 破二道、毘 vs 毗）。
  3. 《尼鈔》性別代詞掃描（他／他們 但本句與前一句無男性指涉詞）。
  4. 標籤與格式全掃（行內標籤黏連、無標籤段、背景標籤殘留、序文標籤一致性）。

用法：
  python -X utf8 _src/book_consistency.py
  python -X utf8 _src/book_consistency.py --book 義鈔
  python -X utf8 _src/book_consistency.py --out 重作材料_長段/全書一致性報告.md
  python -X utf8 _src/book_consistency.py --json 重作材料_長段/全書一致性報告.json
"""
import argparse
import datetime
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {
    '業疏': 'yeshu',
    '戒疏': 'jieshu',
    '尼鈔': 'nicao',
    '行事鈔': 'xingshichao',
    '義鈔': 'yichao',
    '資持記': 'zhichi',
}
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文', '記序')
LEAD_LAB = re.compile(r'^\s*【(%s)】' % '|'.join(LABELS))
BG_TAGS = ('【前文背景', '【後文背景', '【所釋鈔文', '【所釋疏文', '【待審譯文',
           '【分段核驗表】', '【必改硬傷】', '【本次待審')

# 1) 典籍稱謂：正規名 → 同書的其他寫法（含全稱、常見誤展開）
WORK_TERMS = {
    '四分律': ('《四分律》',),
    '母論': ('《母論》',),
    '婆論／婆沙／多論': ('《婆論》', '《婆沙》', '《多論》'),
    '見論': ('《見論》',),
    '雜含': ('《雜含》',),
    '智論': ('《智論》',),
    '善生': ('《善生》',),
    '五百問事': ('《五百問事》', '《五百問事經》'),
    '隨機羯磨': ('《隨機羯磨》',),
}
# 同書異寫（混用偵測）：(分組名, 各寫法)
WORK_VARIANTS = (
    ('毘尼母', ('《毘尼母經》', '《毘尼母論》', '《母論》')),
    ('善見', ('《善見律毘婆沙》', '《善見律》', '《善見論》', '《見論》')),
    ('婆沙', ('《婆沙》', '《婆論》', '《多論》', '《薩婆多毘尼毘婆沙》')),
    ('四分', ('《四分律》', '《四分》')),
)
# 2) 專詞雙軌
TERM_TRACKS = (
    ('波羅夷', ('波羅夷', '斷頭重罪', '他勝處')),
    ('形俱戒', ('形俱戒', '盡形壽戒')),
    ('破內外道', ('破內外道', '破二道', '破內外道戒')),
)
# 3) 尼鈔性別代詞
MALE_REFS = ('比丘', '沙彌', '男子', '俗人', '居士', '父', '賊', '人', '僧', '大僧', '丈夫', '男')
FEMALE_REFS = ('比丘尼', '尼', '女人', '女', '她', '式叉摩那', '沙彌尼')
HE_RE = re.compile(r'他(?:們)?')
HE_SKIP = ('其他', '他人', '他物', '他書', '他典', '他宗', '他部', '他篇', '他日', '他方',
           '他時', '他事', '他處', '他心', '他境', '他緣', '他語', '他本', '他文', '他類')
_HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return ''.join(_HAN.findall(s or ''))


def _parts(row):
    segs = [s for s in (row.get('segments') or [])
            if (s.get('source') or s.get('translation'))]
    if segs:
        return [{'lab': s.get('label') or row.get('label') or '',
                 'orig': s.get('source') or '',
                 'tr': s.get('translation') or ''} for s in segs]
    return [{'lab': row.get('label') or '',
             'orig': row.get('source') or '',
             'tr': row.get('translation') or ''}]


def _sents(text):
    t = re.sub(r'[（(][^）)]*[）)]', '', text or '')
    return [x.strip() for x in re.split(r'(?<=[。！？；\n])', t) if x.strip()]


def scan_book(book):
    p = os.path.join(B, '定稿', BOOKS[book] + '.jsonl')
    if not os.path.exists(p):
        raise SystemExit('找不到定稿：%s' % p)
    term = {}          # 正規名 → 次數
    variant = {}       # 寫法 → 次數
    tracks = {}        # 詞 → 次數
    pi = 0             # 毗
    bi = 0             # 毗（traditional）／毗？
    he = []            # 性別代詞疑例
    label_inline = []  # 行內標籤黏連
    label_missing = []  # 無標籤段
    bg = []
    preface = {}
    mismatch = []      # src 簡稱 vs 譯文異寫
    n_rows = n_parts = 0
    for line in io.open(p, encoding='utf-8'):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        n_rows += 1
        tr_all = row.get('translation') or ''
        src_all = row.get('source') or ''
        parts = _parts(row)
        n_parts += len(parts)
        if tr_all and not LEAD_LAB.match(tr_all):
            label_missing.append(row.get('key'))
        for part in parts:
            tr, src = part['tr'], part['orig']
            if not tr:
                continue
            for norm, forms in WORK_TERMS.items():
                c = sum(tr.count(f) for f in forms)
                if c:
                    term[norm] = term.get(norm, 0) + c
            for gname, forms in WORK_VARIANTS:
                for f in forms:
                    c = tr.count(f)
                    if c:
                        variant[f] = variant.get(f, 0) + c
            for name, forms in TERM_TRACKS:
                hit = [f for f in forms if f in tr]
                if hit:
                    tracks.setdefault(name, {})
                    for f in hit:
                        tracks[name][f] = tracks[name].get(f, 0) + tr.count(f)
            pi += tr.count('\u6bd7')   # 毗
            bi += tr.count('\u6bd8')   # 毘
            # 稱謂對齊：src 有簡稱而譯文只出現展開式
            for norm, forms in WORK_TERMS.items():
                _src_short = norm.split('／')[0]
                if _src_short and _src_short in src:
                    _short_forms = [f for f in forms if f.strip('《》') == _src_short]
                    if _short_forms and not any(f in tr for f in _short_forms):
                        for gname, vforms in WORK_VARIANTS:
                            if any(v in tr for v in vforms):
                                mismatch.append({'key': row.get('key'),
                                                 'src': _src_short,
                                                 'out': [v for v in vforms if v in tr][:2]})
                                break
            # 標籤（無標籤在 row 層已檢查；此處只抓行內黏連）
            for m in re.finditer(r'【(%s)】([^\n]{1})' % '|'.join(LABELS), tr):
                if m.group(2) not in ('\n', ' ', '\u3000'):
                    label_inline.append('%s（%s 後接「%s」）'
                                        % (row.get('key'), m.group(1), m.group(2)))
                    break
            for tag in BG_TAGS:
                if tag in tr:
                    bg.append('%s（%s）' % (row.get('key'), tag.lstrip('【')))
                    break
            for lab_name in ('序文', '疏序', '記序', '會本序'):
                c = tr.count('【%s】' % lab_name)
                if c:
                    preface[lab_name] = preface.get(lab_name, 0) + c
            # 性別代詞（只對尼鈔）
            if book == '尼鈔':
                sents = _sents(tr)
                for i, s in enumerate(sents):
                    _s0 = s
                    for w in HE_SKIP:
                        _s0 = _s0.replace(w, '')
                    if not HE_RE.search(_s0):
                        continue
                    ctx = (sents[i - 1] if i else '') + s
                    if any(w in ctx for w in MALE_REFS):
                        continue
                    if any(w in ctx for w in FEMALE_REFS):
                        he.append({'key': row.get('key'), 'sent': s[:80]})
    return {'book': book, 'file': '定稿/%s.jsonl' % BOOKS[book],
            'rows': n_rows, 'parts': n_parts,
            'terms': term, 'variants': variant, 'tracks': tracks,
            'pi': pi, 'bi': bi, 'he': he,
            'label_inline': label_inline, 'label_missing': label_missing,
            'bg': bg, 'preface': preface, 'mismatch': mismatch}


def _row_table(headers, rows):
    L = ['| ' + ' | '.join(headers) + ' |',
         '|' + '|'.join(':' + '-' * max(2, len(h) * 2) for h in headers) + '|']
    for r in rows:
        L.append('| ' + ' | '.join(str(x) for x in r) + ' |')
    return L


def write_report(path, results, generated):
    L = ['# 全書一致性報告（book_consistency）', '',
         '- 產生時間：%s' % generated,
         '- 來源：`定稿/*.jsonl`（只讀；本報告不寫任何定稿／docs）',
         '- 性質：0 成本統計，只列清單，不自動改譯文。', '']
    L += ['## 一、典籍稱謂統計', '',
          '> 同一部書在同一本譯文內出現多種寫法者，交由 `norm.py` 批次統一；'
          '下列數字供人工核對「是否与原文簡稱相符」。', '']
    for r in results:
        L.append('### %s' % r['book'])
        L.append('')
        rows = [(k, v) for k, v in sorted(r['terms'].items(), key=lambda x: -x[1])]
        L += _row_table(('稱謂', '次數'), rows) if rows else ['（無）']
        L.append('')
        vr = [(k, v) for k, v in sorted(r['variants'].items(), key=lambda x: -x[1])]
        if vr:
            L += ['**同書異寫**：', ''] + _row_table(('寫法', '次數'), vr) + ['']
        if r['mismatch']:
            L += ['**原文簡稱與譯文異寫（前 20）**：', '']
            for m in r['mismatch'][:20]:
                L.append('- %s：原文「%s」→ 譯文 %s' % (m['key'], m['src'], '／'.join(m['out'])))
            L.append('')
    L += ['## 二、高頻專詞雙軌', '',
          '> 同一本內並存兩種譯法時，依全書多數例或專家標準統一（本程式不自動替換）。', '']
    for r in results:
        if not r['tracks']:
            continue
        L.append('### %s' % r['book'])
        for name, forms in r['tracks'].items():
            L.append('- **%s**：%s' % (name, '；'.join('%s %d 次' % (f, c)
                                                     for f, c in sorted(forms.items(), key=lambda x: -x[1]))))
        L.append('- 毗（U+6BD7）／毘（U+6BD8）用字：%d／%d 次（若同一本混用，交 `norm.py` 統一）'
                 % (r['pi'], r['bi']))
        L.append('')
    L += ['## 三、《尼鈔》性別代詞掃描', '',
          '> 條件：句含「他／他們」，但本句與前一句皆無男性指涉詞；僅列清單，待人工判定。', '']
    _n = 0
    for r in results:
        if r['book'] != '尼鈔':
            continue
        _n = len(r['he'])
        L.append('疑似誤用男性代詞：%d 句' % _n)
        for x in r['he'][:50]:
            L.append('- %s：%s' % (x['key'], x['sent']))
        L.append('')
    if not _n:
        L += ['- 無。', '']
    L += ['## 四、標籤與格式', '']
    for r in results:
        L.append('### %s' % r['book'])
        L.append('')
        L.append('- 行內標籤黏連：%d 例' % len(r['label_inline']))
        for x in r['label_inline'][:10]:
            L.append('  - %s' % x)
        L.append('- 無標籤段：%d 例%s' % (
            len(r['label_missing']),
            ('（' + '、'.join(str(k) for k in r['label_missing'][:10]) + '）')
            if r['label_missing'] else ''))
        L.append('- 背景標籤殘留：%d 例' % len(r['bg']))
        for x in r['bg'][:10]:
            L.append('  - %s' % x)
        L.append('- 序文標籤：%s' % ('；'.join('%s %d' % (k, v)
                                             for k, v in sorted(r['preface'].items()))
                                   or '（無）'))
        L.append('')
    L += ['## 說明', '',
          '- 本報告只做統計與列名，不判定對錯、不改 `定稿/*.jsonl`。',
          '- 稱謂統一、簡稱還原、孤立引號等確定性修正由 `norm.py` 執行；'
          '專詞雙軌與性別代詞須人工確認後再改。',
          '']
    io.open(path, 'w', encoding='utf-8').write('\n'.join(L))


def main():
    ap = argparse.ArgumentParser(
        description='全書一致性統計（稱謂／專詞／性別代詞／標籤；只報告）')
    ap.add_argument('--book', default='全部', choices=list(BOOKS) + ['全部'])
    ap.add_argument('--out', default='重作材料_長段/全書一致性報告.md')
    ap.add_argument('--json', default='', help='另存 JSON（選填）')
    args = ap.parse_args()
    books = list(BOOKS) if args.book == '全部' else [args.book]
    results = [scan_book(b) for b in books]
    for r in results:
        print('%-5s %5d 筆／%5d 段｜稱謂 %d 種｜異寫 %d 種｜代詞疑例 %d｜行內標籤 %d｜無標籤 %d｜背景 %d'
              % (r['book'], r['rows'], r['parts'], len(r['terms']), len(r['variants']),
                 len(r['he']), len(r['label_inline']), len(r['label_missing']), len(r['bg'])))
    generated = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    out = args.out
    if out and not os.path.isabs(out):
        out = os.path.join(B, out.replace('/', os.sep))
    if out:
        d = os.path.dirname(out)
        if d:
            os.makedirs(d, exist_ok=True)
        write_report(out, results, generated)
        print('報告 → %s' % out)
    if args.json:
        jp = args.json if os.path.isabs(args.json) else os.path.join(B, args.json.replace('/', os.sep))
        io.open(jp, 'w', encoding='utf-8').write(
            json.dumps({'generated': generated, 'results': results},
                       ensure_ascii=False, indent=1))
        print('JSON → %s' % jp)


if __name__ == '__main__':
    main()
