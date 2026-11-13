# -*- coding: utf-8 -*-
"""機械層檢查與修復：疊字、標點、括號、引號、專名。

用法：
  python _src/mech_check.py            # 只檢查，輸出報告
  python _src/mech_check.py --fix      # 自動修復可安全修復者
  python _src/mech_check.py --book 02_戒疏
"""
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
REPORT = os.path.join(B, '測試', '機械層報告.md')

# 合法的疊字／疊詞（不報）
WHITELIST = [
    '了了分明', '實實在在', '是是非非', '在在家人', '明明了了', '各各', '一一',
    '種種', '時時', '處處', '漸漸', '往往', '剛剛', '常常', '天天', '多多',
    '少少', '小小', '高高', '低低', '深深', '淺淺', '久久', '早早', '晚晚',
]

# 疊字／疊詞（確定該報）
DUP_PATTERNS = [
    (r'的緣故的緣故', '疊句'),
    (r'所以所以', '疊詞'),
    (r'因為因為', '疊詞'),
    (r'如果如果', '疊詞'),
    (r'但是但是', '疊詞'),
    (r'就是就是', '疊詞'),
    (r'的的(?![們])', '疊字'),
    (r'了了(?!分明)', '疊字'),
    (r'是是(?![非])', '疊字'),
    (r'在在(?!家人)', '疊字'),
]

# 標點問題
PUNCT_PATTERNS = [
    (r'。。', '雙句號', '。'),
    (r'，，', '雙逗號', '，'),
    (r'。，', '句逗連用', '。'),
    (r'，，', '雙逗號', '，'),
    (r'、、', '雙頓號', '、'),
    (r'；；', '雙分號', '；'),
    (r'：：', '雙冒號', '：'),
]

# 專名（需統一的寫法 → 建議）
PROPER = {
}



# 夾註衝突檢查：同一 chunk 前後 3 段對同一術語的夾註若釋義不同即報
ANN_PAT = re.compile(r'[（(]([^）)]{2,20})[）)]')


def check_annotation_conflicts(t):
    """回傳 [(括註文字, 段序, 段序)] 衝突清單。"""
    paras = [x for x in re.split(r'\r?\n\r?\n', t) if x.strip()]
    out = []
    seen = {}
    for i, para in enumerate(paras):
        for m in ANN_PAT.finditer(para):
            ann = m.group(1).strip()
            if '即' not in ann and '＝' not in ann:
                continue
            # 取括註中被解釋的術語（前 2-4 字）
            key = ann[:4]
            if key in seen and seen[key][0] != ann:
                j, prev = seen[key]
                if i - j <= 3:
                    out.append((key, j + 1, i + 1, prev, ann))
            seen.setdefault(key, (i, ann))
    return out


def load_books(only_book=None):
    for book in sorted(os.listdir(OUT)):
        d = os.path.join(OUT, book)
        if not os.path.isdir(d):
            continue
        if only_book and book != only_book:
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith('.txt'):
                yield book, f, os.path.join(d, f)


def scan_text(t):
    hits = []
    for pat, kind in DUP_PATTERNS:
        for m in re.finditer(pat, t):
            ctx = t[max(0, m.start() - 30):m.end() + 30].replace('\n', ' ')
            if any(w in ctx for w in WHITELIST):
                continue
            hits.append((kind, pat, m.group(0), ctx, m.start()))
    for pat, kind, _ in PUNCT_PATTERNS:
        for m in re.finditer(re.escape(pat), t):
            ctx = t[max(0, m.start() - 30):m.end() + 30].replace('\n', ' ')
            hits.append((kind, pat, m.group(0), ctx, m.start()))
    for k, v in PROPER.items():
        for m in re.finditer(re.escape(k), t):
            ctx = t[max(0, m.start() - 30):m.end() + 30].replace('\n', ' ')
            hits.append(('專名', k, v, ctx, m.start()))
    for key, a, b, pa, pb in check_annotation_conflicts(t):
        hits.append(('夾註衝突', key, '%s vs %s' % (pa, pb), '段 %d/%d' % (a, b), -1))
    # 括號／引號配對
    for op, cl, name in (('（', '）', '圓括號'), ('「', '」', '引號'), ('『', '』', '雙引號')):
        if t.count(op) != t.count(cl):
            hits.append(('配對', name, '%d/%d' % (t.count(op), t.count(cl)), '', -1))
    return hits


def main():
    fix = '--fix' in sys.argv
    only_book = None
    if '--book' in sys.argv:
        only_book = sys.argv[sys.argv.index('--book') + 1]

    total = Counter()
    rows = []
    for book, f, path in load_books(only_book):
        t = io.open(path, encoding='utf-8').read()
        orig = t
        hits = scan_text(t)
        if not hits:
            continue
        for kind, pat, got, ctx, pos in hits:
            total[kind] += 1
            rows.append((book, f, kind, got, ctx))
        if fix:
            t2 = t
            for pat, kind, rep in PUNCT_PATTERNS:
                t2 = t2.replace(pat, rep)
            for pat, kind in DUP_PATTERNS:
                # 疊字修復：重複字只留一個
                t2 = re.sub(pat, lambda m: m.group(0)[:max(1, len(m.group(0)) // 2)], t2)
            if t2 != orig:
                bak = os.path.join(B, '歸檔', '機械層修正前', book + '__' + f)
                os.makedirs(os.path.dirname(bak), exist_ok=True)
                if not os.path.exists(bak):
                    io.open(bak, 'w', encoding='utf-8', newline='').write(orig)
                io.open(path, 'w', encoding='utf-8', newline='').write(t2)

    lines = ['# 機械層檢查報告', '', '共 %d 處' % sum(total.values()), '',
             '| 類型 | 處數 |', '|:--|--:|']
    for k, v in total.most_common():
        lines.append('| %s | %d |' % (k, v))
    lines += ['', '## 明細', '']
    seen = set()
    for book, f, kind, got, ctx in rows:
        key = (book, f, kind, got)
        if key in seen:
            continue
        seen.add(key)
        lines.append('- **%s/%s**（%s）`%s` …%s…' % (book, f, kind, got, ctx))
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    io.open(REPORT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('檢查完成：%d 處，報告 %s' % (sum(total.values()), REPORT))
    for k, v in total.most_common():
        print('  %-8s %d' % (k, v))


if __name__ == '__main__':
    main()
