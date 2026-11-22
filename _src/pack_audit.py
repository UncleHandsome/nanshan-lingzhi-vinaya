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

PACK_MAX = 450
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
    _nat = lambda f: re.sub(r'\d+', lambda m: m.group(0).zfill(8), f)
    for fn in sorted(os.listdir(jd), key=_nat):
        if not fn.endswith('.md'):
            continue
        key = fn[:-3]
        md = MI.load(jd, key) or {}
        body = ''
        rp = os.path.join(rep, key + '_回.txt')
        if os.path.exists(rp):
            _rt = ''
            try:
                _rt = io.open(rp, encoding='utf-8').read()
                body = A.col3(_rt) or ''
                if MI.is_keep_a(body):
                    body = MI.from_jia(io.open(os.path.join(jd, key + '.md'), encoding='utf-8').read())
            except Exception:
                body = ''
            if not (body or '').strip():
                if 'PASS_A' in _rt:
                    body = MI.from_jia(io.open(os.path.join(jd, key + '.md'), encoding='utf-8').read())
                if not (body or '').strip():
                    print('  ⚠ 裁決回覆無譯文，審核包留空：', key)
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
        def _idx(s):
            try:
                return int(s.rsplit('_', 1)[-1])
            except Exception:
                return None
        _pm, _cm = cur[-1]['md'] if cur else {}, it['md']
        _ps, _cs = _pm.get('s0'), _cm.get('s0')
        _pg, _cg = _pm.get('g1'), _cm.get('g1')
        if _ps is not None and _cs is not None:
            _adj = (_cs == _pg) if _pg is not None else (_cs > _ps)
        else:
            _pi, _ci = _idx(cur[-1]['key']) if cur else None, _idx(it['key'])
            _adj = _pi is not None and _ci is not None and 0 < _ci - _pi <= 10
        _labs_it = tuple(sorted({u['lab'] for u in it['md'].get('units', []) if u.get('lab')}))
        _labs_pv = tuple(sorted({u['lab'] for u in _pm.get('units', []) if u.get('lab')})) if cur else _labs_it
        same = (not cur) or (cur[-1]['md'].get('ex', '').split('，')[0]
                             == it['md'].get('ex', '').split('，')[0] and _adj and _labs_it == _labs_pv)
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
        _labs = set()
        for _it in pack:
            for _u in (_it['md'].get('units') or []):
                if _u.get('lab'):
                    _labs.add(_u['lab'])
        _src = ''.join((_u.get('orig') or '') for _it in pack
                       for _u in (_it['md'].get('units') or []))
        _long = any(it['md'].get('long') for it in pack)
        _notes = BC.notes_for(_book, _labs, _src, body, long=_long,
                              key=pack[0]['key'])
        _prompt = MA.render_audit(_notes['book_note'], _notes['dual_note'],
                                  _notes['long_note'], extra=_notes)
        L = [_prompt, '', '---', '', '（出處：%s）' % pack[0]['md'].get('ex', ''), '']
        _packed = len(pack) > 1 or bool(pack[0]['md'].get('packed'))
        pre = pack[0]['md'].get('pre', '')
        post = pack[-1]['md'].get('post', '')
        if pre:
            L += ['【前文背景（僅供參考，嚴禁譯入正文）】', '', pre, '']
        if _packed:
            L += ['【分段要求】本單元含多個短段，請按 [1][2]… 編號逐條核對；包內 [1]..[n] 原屬相鄰上下文，判讀代詞與承接關係時請相互參照，輸出時仍依各編號獨立對應。', '']
        L += ['【原文】', '']
        for idx_u, it in enumerate(pack, 1):
            _pfx = ('[%d]' % idx_u) if len(pack) > 1 else ''
            for u in it['md'].get('units', []):
                L += ['■ %s（原文）%s' % (u['lab'], _pfx), '', u['orig'], '']
        L += ['【待審譯文】', '', body, '']
        if post:
            L += ['【後文背景（僅供參考，嚴禁譯入正文）】', '', post, '']
        _mchs = [(i, (it['md'].get('mother') or '').strip()) for i, it in enumerate(pack, 1)
                 if (it['md'].get('mother') or '').strip()]
        _mseen, _mchs2 = set(), []
        for i, m in _mchs:
            if m not in _mseen:
                _mseen.add(m); _mchs2.append((i, m))
        _mchs = _mchs2
        if _mchs:
            L += ['【所釋鈔文（僅供對照，嚴禁譯入正文）】', '']
            for i, m in _mchs:
                L += [(('[%d] ' % i) if len(pack) > 1 else '') + m, '']
        io.open(os.path.join(out, key + '.md'), 'w', encoding='utf-8').write('\n'.join(L))
        # 單一成員且原已打包時，沿用原 segments（否則下游會以 1 段對多個 [n]）
        if len(pack) == 1 and pack[0]['md'].get('packed') and pack[0]['md'].get('segments'):
            _segs = list(pack[0]['md']['segments'])
        else:
            _segs = [it['body'] for it in pack]
        MI.write_json(out, key, {
            'key': key,
            'book': pack[0]['md'].get('book', ''),
            'pre': pre, 'post': post,
            'units': [dict(u, pack_idx=i) for i, it in enumerate(pack, 1)
                      for u in it['md'].get('units', [])],
            'packed': _packed,
            'segments': _segs,
            'members': [it['key'] for it in pack],
            'mother': '\n'.join((('[%d] ' % i) if len(pack) > 1 else '') + m for i, m in _mchs),
        })

    io.open(os.path.join(out, '索引_pack.json'), 'w', encoding='utf-8').write(
        json.dumps(mapping, ensure_ascii=False, indent=1))
    print('打包完成：%d 個單位（其中 %d 個為多段包）→ %s'
          % (len(mapping), n_pack, os.path.relpath(out, B)))


if __name__ == '__main__':
    main()
