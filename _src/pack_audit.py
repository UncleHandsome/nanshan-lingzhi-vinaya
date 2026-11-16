# -*- coding: utf-8 -*-
"""舊格式批次：把相鄰短組打包成一個審核單位（審閱／修訂／合併一起打包）。

用法：
  python -X utf8 _src/pack_audit.py --judge 測試/實驗11/_L7_裁決 --out 測試/_pack_審核
"""
import argparse
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import materials_io as MI  # noqa: E402
import book_config as BC  # noqa: E402
import build_a2 as A      # noqa: E402
import mk_audit_materials as MA  # noqa: E402

PACK_MAX = 300
PACK_SEGS = 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--judge', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--max', type=int, default=PACK_MAX)
    ap.add_argument('--segs', type=int, default=PACK_SEGS)
    args = ap.parse_args()

    jd = os.path.join(B, args.judge.replace('/', os.sep))
    rep = os.path.join(jd, '回覆')
    out = os.path.join(B, args.out.replace('/', os.sep))
    os.makedirs(out, exist_ok=True)
    for f in list(os.listdir(out)):
        if f.endswith(('.md', '.json')):
            os.remove(os.path.join(out, f))

    items = []
    for fn in sorted(os.listdir(jd)):
        if not fn.endswith('.md'):
            continue
        key = fn[:-3]
        md = MI.load(jd, key) or {}
        body = ''
        rp = os.path.join(rep, key + '_回.txt')
        if os.path.exists(rp):
            try:
                _rt = io.open(rp, encoding='utf-8').read()
                body = A.col3(_rt) or ''
                if MI.is_keep_a(body):
                    body = MI.from_jia(io.open(os.path.join(jd, key + '.md'), encoding='utf-8').read())

            except Exception:
                body = ''
        items.append(dict(key=key, md=md, body=body))

    packs, cur, cur_len = [], [], 0
    for it in items:
        if it['md'].get('packed'):
            if cur:
                packs.append(cur)
                cur, cur_len = [], 0
            packs.append([it])
            continue
        ln = len(it['body'])
        same = (not cur) or (cur[-1]['md'].get('ex', '').split('，')[0]
                             == it['md'].get('ex', '').split('，')[0])
        if cur and (not same or cur_len + ln > args.max or len(cur) >= args.segs):
            packs.append(cur)
            cur, cur_len = [], 0
        cur.append(it)
        cur_len += ln
    if cur:
        packs.append(cur)

    mapping = {}
    n_pack = 0
    for idx, pack in enumerate(packs, 1):
        if len(pack) == 1:
            it = pack[0]
            shutil_copy = it['body']
            key = it['key']
            mapping[key] = [key]
        else:
            key = '%s_pack%02d' % (pack[0]['md'].get('ex', 'x').split('，')[0], idx)
            key = re.sub(r'[^\w\u4e00-\u9fff]', '', key)
            mapping[key] = [it['key'] for it in pack]
            n_pack += 1
        lines = []
        if len(pack) == 1:
            lines.append(pack[0]['body'])
        else:
            for n, it in enumerate(pack, 1):
                lines.append('[%d] %s' % (n, it['body'].strip()))
        body = '\n\n'.join(lines)

        _book = pack[0]['md'].get('book') or BC.book_of(os.path.join(jd, pack[0]['key'] + '.md'))
        _cfg = BC.cfg(_book)
        _prompt = (MA.AUDIT_PROMPT.replace('{book_note}', _cfg.get('note', ''))
                    .replace('{dual_note}', '').replace('{long_note}', ''))
        L = [_prompt, '', '---', '', '（出處：%s）' % pack[0]['md'].get('ex', ''), '']
        pre = pack[0]['md'].get('pre', '')
        post = pack[-1]['md'].get('post', '')
        if pre:
            L += ['【前文背景（僅供參考）】', '', pre, '']
        if len(pack) > 1:
            L += ['【分段要求】本單元含多個短段，請保留 [1][2]… 編號逐條對應，勿合併增減。', '']
        L += ['【原文】', '']
        for it in pack:
            for u in it['md'].get('units', []):
                L += ['■ %s（原文）' % u['lab'], '', u['orig'], '']
        L += ['【待審譯文】', '', body, '']
        if post:
            L += ['【後文背景（僅供參考）】', '', post, '']
        io.open(os.path.join(out, key + '.md'), 'w', encoding='utf-8').write('\n'.join(L))
        MI.write_json(out, key, {
            'key': key,
            'book': pack[0]['md'].get('book', ''),
            'pre': pre, 'post': post,
            'units': [u for it in pack for u in it['md'].get('units', [])],
            'packed': len(pack) > 1,
            'segments': [it['body'] for it in pack],
            'members': [it['key'] for it in pack],
        })

    io.open(os.path.join(out, '索引_pack.json'), 'w', encoding='utf-8').write(
        json.dumps(mapping, ensure_ascii=False, indent=1))
    print('打包完成：%d 個單位（其中 %d 個為多段包）→ %s'
          % (len(mapping), n_pack, os.path.relpath(out, B)))


if __name__ == '__main__':
    main()
