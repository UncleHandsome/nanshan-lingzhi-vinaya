# -*- coding: utf-8 -*-
import io, json, os, re, html
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '重作材料_長段', 'alignment')
BOOKS = {
    'xingshichao': ('行事鈔', ('卷上', '卷中', '卷下'), 'TXT/01_四分律刪繁補闕行事鈔.txt'),
    'yichao': ('義鈔', ('卷上', '卷中'), 'TXT/05_四分律拾毗尼義鈔.txt'),
}

def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def main():
    os.makedirs(OUT, exist_ok=True)
    summary = []
    for book, (name, vols, rawp) in BOOKS.items():
        raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
        h = ''
        for c in raw:
            if re.match(r'[\u4e00-\u9fff]', c):
                h += c
        recs = []
        miss = order = 0
        for v in vols:
            t = io.open(os.path.join(B, 'docs', book, v + '.html'), encoding='utf-8').read()
            cursor = 0
            idx = 0
            for m in re.finditer(r'<div class="pair[^"]*"[^>]*><div class="o[^"]*">(.*?)</div>', t, re.S):
                idx += 1
                s = han(html.unescape(re.sub('<[^>]+>', '', m.group(1))))
                if not s:
                    continue
                q = h.find(s[:20], cursor)
                if q < 0:
                    q = h.find(s[:12], cursor)
                if q < 0:
                    q = h.find(s[:8], cursor)
                if q < 0:
                    q = h.find(s[:20])
                if q < 0:
                    q = h.find(s[:12])
                if q < 0:
                    q = h.find(s[:8])
                if q < 0:
                    miss += 1
                    continue
                if q < cursor:
                    order += 1
                recs.append({'key': '%s-%03d' % (v, idx), 'pos': q, 'len': len(s)})
                cursor = max(cursor, q + 1)
        cover = [0] * len(h)
        for r in recs:
            for i in range(r['pos'], min(r['pos'] + r['len'], len(h))):
                cover[i] += 1
        gaps = 0
        i = 0
        while i < len(h):
            if cover[i] == 0:
                j = i
                while j < len(h) and cover[j] == 0:
                    j += 1
                if j - i >= 20:
                    gaps += 1
                i = j
            else:
                i += 1
        dups = sum(1 for r in recs if any(cover[i] > 1 for i in range(r['pos'], min(r['pos'] + r['len'], len(h)))))
        data = {'book': name, 'pairs': len(recs), 'miss': miss, 'order_break': order, 'gaps': gaps, 'overlaps': dups, 'records': recs}
        json.dump(data, io.open(os.path.join(OUT, book + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        summary.append((name, len(recs), miss, order, gaps, dups))
        print('%s pairs=%d miss=%d order=%d gaps=%d overlaps=%d' % (name, len(recs), miss, order, gaps, dups))
    with io.open(os.path.join(OUT, '行事鈔_義鈔_摘要.md'), 'w', encoding='utf-8') as f:
        f.write('# 行事鈔、義鈔 sequential alignment\n\n| 書 | pairs | 找不到 | 順序倒退 | 缺口 | 重疊 |\n|:--|--:|--:|--:|--:|--:|\n')
        for row in summary:
            f.write('| %s | %d | %d | %d | %d | %d |\n' % row)

if __name__ == '__main__':
    main()
