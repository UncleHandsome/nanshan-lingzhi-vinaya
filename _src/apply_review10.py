# -*- coding: utf-8 -*-
"""套用十筆最長段試跑結果（含人工修正 114、16b）。

- 4 筆 fixed：照千問修正套用（尼鈔496、尼鈔770、資持記1036、義鈔GAP13-11）
- 業疏16b_卷三之五_0024-2：採用千問 3 處修正，但「隨作感業」一處依人工判決回退為
  「隨著身口動作而生起業」與「隨著使用事物造作而感得業」，不採用「所作之物被受用」。
- 義鈔114（uncertain）：人工定案——首答改為「這條戒（長衣戒）…與急施衣戒不同」，
  並移除末段夾疏括號。
"""
import io
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
import run_3k_review as R

B = R.B


def load_tr(result_path, mk):
    t = io.open(result_path, encoding='utf-8').read()
    blocks = re.findall(r'<<<JSONL_START>>>(.*?)<<<JSONL_END>>>', t, re.S)
    for ln in blocks[-1].strip().splitlines():
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if R.match_key(o.get('key'), [mk]) == mk:
            return (o.get('translation') or '').strip()
    return ''


def manual_114(old):
    tr = old.replace('答：這條戒不論在衣時或非衣時都會結犯，所以與長衣戒不同。',
                     '答：這條戒（長衣戒）在衣時或非衣時都會結犯，所以與急施衣戒不同。')
    tr = tr.replace('（那十日只開畜長衣，不開離衣出界）', '')
    return tr


def adjust_16b(qwen_tr):
    tr = qwen_tr.replace(
        '問：疏中「隨著身口動作而生起業」（作俱無作）與「隨著所作之物被受用而感得業」（從用無作），畢竟相互混濫，要如何區分？',
        '問：疏中「隨著身口動作而生起業」與「隨著使用事物造作而感得業」，畢竟相互混濫，要如何區分？')
    return tr


def main():
    apply = '--apply' in sys.argv
    keymap = R.all_segment_keys()          # kid -> (book,rowkey,si,label,seg)
    fixes = {}

    def kid(book, mk):
        k = '%s|%s' % (book, mk)
        if k not in keymap:
            raise SystemExit('key not found: ' + k)
        return k

    base = r'抽樣_最長兩段_20261124'
    for book, mk in [('nicao', '496'), ('nicao', '770'), ('zhichi', '1036'), ('yichao', 'GAP13-11')]:
        import book_prompt
        label = book_prompt.PROFILES[book]['name']
        prefix = '%s_%s_' % (label, mk.replace('/', '_'))
        cand = [f for f in os.listdir(base)
                if f.startswith(prefix) and '輸入與結果' in f]
        if not cand:
            raise SystemExit('result file not found for ' + prefix)
        path = os.path.join(base, cand[0])
        tr = load_tr(path, mk)
        fixes[kid(book, mk)] = tr
        print('Qwen', book, mk, 'len', len(tr))

    cand16 = [f for f in os.listdir(base)
              if f.startswith('業疏_16b_卷三之五_0024-2_') and '輸入與結果' in f]
    if not cand16:
        raise SystemExit('result file not found for 16b')
    p16 = os.path.join(base, cand16[0])
    q16 = load_tr(p16, '16b_卷三之五_0024-2')
    t16 = adjust_16b(q16)
    assert '所作之物被受用' not in t16
    fixes[kid('yeshu', '16b_卷三之五_0024-2')] = t16
    print('Qwen16b adjusted len', len(t16))

    k114 = kid('yichao', '114')
    old114 = keymap[k114][4].get('translation') or ''
    t114 = manual_114(old114)
    assert '與急施衣戒不同' in t114 and '不開離衣出界' not in t114
    fixes[k114] = t114
    print('manual114 len', len(t114))

    # label 前綴對齊：舊譯若無【label】則去掉新譯的【label】
    for k, tr in fixes.items():
        book, rowkey, si, lab, seg = keymap[k]
        old = seg.get('translation') or ''
        if not old.startswith('【'):
            m = re.match(r'^【([^】]{1,4})】\s*\n?', tr)
            if m and m.group(1) == (seg.get('label') or lab):
                fixes[k] = tr[m.end():].lstrip()
        print('FIX', book, rowkey, si, 'old', len(old), 'new', len(fixes[k]))

    if not apply:
        print('dry-run only; add --apply')
        return
    bybook = {}
    for k, tr in fixes.items():
        book, rowkey, si, lab, seg = keymap[k]
        bybook.setdefault(book, []).append((rowkey, si, tr))
    for book, fs in bybook.items():
        path = os.path.join(B, '定稿', book + '.jsonl')
        bak = path + '.bak_review10_20261124'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
        bykey = {str(r['key']): r for r in rows}
        for rowkey, si, tr in fs:
            r = bykey[rowkey]
            segs = r['segments']
            segs[si - 1]['translation'] = tr
            r['translation'] = '\n\n'.join((s.get('translation') or '') for s in segs)
        io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
            json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
        print('applied', book, len(fs))


if __name__ == '__main__':
    main()
