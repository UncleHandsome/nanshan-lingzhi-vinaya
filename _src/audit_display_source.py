# -*- coding: utf-8 -*-
"""全書 display_source 截斷檢查：分類 marker／front matter／標點／真截斷，並批次修可確定者。"""
import io, json, os, re, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [('xingshichao', '行事鈔'), ('jieshu', '戒疏'), ('yeshu', '業疏'),
         ('nicao', '尼鈔'), ('yichao', '義鈔'), ('zhichi', '資持記')]
REPORT = os.path.join(B, '重作材料_長段', '顯示層邊界_全書檢查.md')


def load(b):
    p = os.path.join(B, '定稿', b + '.jsonl')
    return [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]


def strip_markers(s):
    s = (s or '').replace('\u3000', ' ').strip()
    s = re.sub(r'\[\d+\]\s*', '', s)
    return re.sub(r'\s+', '', s)


def norm(s):
    s = strip_markers(s)
    s = re.sub(r'[。！？…」』）〕：:；;，,、]+$', '', s)
    return s


def main(apply=False):
    out = ['# 全書 display_source 截斷檢查', '', '只比較 `source` 與 `display_source`；分類後只修可確定者。', '']
    total = fixed = 0
    for b, name in BOOKS:
        rows = load(b)
        stats = {'marker': [], 'front': [], 'punct': [], 'trunc': [], 'empty': 0}
        for r in rows:
            s = (r.get('source') or '').strip()
            d = (r.get('display_source') or '').strip()
            if not s:
                continue
            total += 1
            if not d:
                stats['empty'] += 1
                continue
            if len(d) >= len(s) * 0.8:
                continue
            if strip_markers(s) == strip_markers(d):
                # 只差 [1] 標記；保留 display（較乾淨），不硬塞 [n]
                stats['marker'].append(r['key'])
                continue
            if (s.startswith('底本：') or s.startswith('No.') or re.match(r'^No\.\s*\d', s)) and not d.startswith(('底本：', 'No.')):
                stats['front'].append(r['key'])
            elif norm(s) == norm(d):
                stats['punct'].append(r['key'])
            else:
                stats['trunc'].append(r['key'])
        out += ['## %s' % name, '', '```text',
                'rows %d' % len(rows),
                'empty %d' % stats['empty'],
                'marker-only %d' % len(stats['marker']),
                'front-matter %d' % len(stats['front']),
                'punct-only %d' % len(stats['punct']),
                'real-trunc %d' % len(stats['trunc']),
                '```', '']
        for k in stats['marker'][:10]:
            out.append('- marker: `%s`' % k)
        for k in stats['front'][:20]:
            out.append('- front: `%s`' % k)
        for k in stats['punct'][:20]:
            out.append('- punct: `%s`' % k)
        for k in stats['trunc'][:20]:
            out.append('- trunc: `%s`' % k)
        out.append('')
        if apply:
            for r in rows:
                if r['key'] not in stats['front'] + stats['punct'] + stats['trunc']:
                    continue
                s = (r.get('source') or '').strip()
                r['display_source'] = s
                for seg in r.get('segments') or []:
                    if (seg.get('source') or '').strip():
                        seg['display_source'] = seg.get('source', '').strip()
                fixed += 1
        # 寫回（即使 apply=False 也不寫）
        if apply:
            p = os.path.join(B, '定稿', b + '.jsonl')
            io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    out += ['## 合計', '', '```text', 'rows %d' % total, 'fixed %d' % fixed, '```', '']
    io.open(REPORT, 'w', encoding='utf-8').write('\n'.join(out))
    print('total', total, 'fixed', fixed, 'report', REPORT)


if __name__ == '__main__':
    main('--apply' in sys.argv)
