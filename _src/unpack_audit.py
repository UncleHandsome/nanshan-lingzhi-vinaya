# -*- coding: utf-8 -*-
"""審後拆回：將 _打包審核/回覆 依【必改硬傷】行首 [n] 拆回單段 _終審_拆回/回覆。

用法：
  python -X utf8 _src/unpack_audit.py --pack 測試/重譯/資持記/_打包審核 --out 測試/重譯/資持記/_終審_拆回
"""
import argparse
import io
import json
import os
import re
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
if os.path.join(B, '_src') not in sys.path:
    sys.path.insert(0, os.path.join(B, '_src'))

import materials_io as MI  # noqa: E402

_NUM_EXPR = r'\[\s*\d+(?:\s*[-–—~～,，、]\s*\d+)*\s*\]'
_LEAD_RE = re.compile(
    r'^\s*(?:[-*•]|\d+[.、．])?\s*'
    r'((?:(?:\*\*|__)?\s*' + _NUM_EXPR + r'\s*(?:\*\*|__)?(?:\s*[,，、及與]\s*)?)+)'
    r'[:：]?\s*'
)
_BRACKET_RE = re.compile(_NUM_EXPR)
_BULLET_RE = re.compile(r'^\s*(?:[-*•]|\d+[.、．])\s+')
_CONT_RE = re.compile(r'^(?:\s{2,}|\t|(?:問題|依據|修正方向|→)[：:])')


def _resolve(p):
    p = p.replace('/', os.sep)
    return p if os.path.isabs(p) else os.path.join(B, p)


def _fixes_block(rt):
    m = re.search(
        r'【必改硬傷】(.+?)(?=【(?:可斟酌微瑕|微瑕|附註|建議|備註)】|\n\s*\**\s*4[.、．：:]|\Z)',
        rt, re.S)
    if m:
        return m.group(1).strip()
    m2 = re.search(
        r'必改硬傷\**[:：]?\s*(.+?)(?=【(?:可斟酌微瑕|微瑕|附註|建議|備註)】|\n\s*\**\s*4[.、．：:]|\Z)',
        rt, re.S)
    return m2.group(1).strip() if m2 else ''


def _parse_indices(prefix, n_members):
    out = []
    for expr in _BRACKET_RE.findall(prefix):
        inner = expr.strip()[1:-1].strip()
        for part in re.split(r'\s*[,，、]\s*', inner):
            if not part:
                continue
            m = re.fullmatch(r'(\d+)\s*[-–—~～]\s*(\d+)', part)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                if a > b:
                    a, b = b, a
                if a < 1 or b > n_members:
                    return None
                for k in range(a, b + 1):
                    if k not in out:
                        out.append(k)
            elif part.isdigit():
                k = int(part)
                if k < 1 or k > n_members:
                    return None
                if k not in out:
                    out.append(k)
            else:
                return None
    return out if out else None


def _split_fix_items(fixes_txt, n_members):
    items = []
    active_group = None
    for raw_ln in (fixes_txt or '').splitlines():
        ln = raw_ln.rstrip()
        if not ln.strip():
            continue
        m = _LEAD_RE.match(ln)
        if m:
            idxs = _parse_indices(m.group(1), n_members)
            rem = ln[m.end():].strip()
            if not rem:
                active_group = idxs
                continue
            active_group = None
            items.append([idxs, '- ' + rem])
            continue
        if items and _CONT_RE.match(raw_ln):
            items[-1][1] += '\n' + ln.strip()
            continue
        if active_group is not None:
            clean = _BULLET_RE.sub('', ln).strip()
            items.append([list(active_group), '- ' + clean])
            continue
        clean = _BULLET_RE.sub('', ln).strip()
        if clean and clean not in ('無', '無。'):
            items.append([None, '- ' + clean])
    return [(idxs, txt) for idxs, txt in items]


def _write_pass(dst_path):
    io.open(dst_path, 'w', encoding='utf-8').write('【結論】\nPASS\n\n【必改硬傷】\n無\n')


def _write_fix(dst_path, lines):
    body = '\n'.join(lines).strip()
    io.open(dst_path, 'w', encoding='utf-8').write('【結論】\nFIX\n\n【必改硬傷】\n%s\n' % body)


def _sync_evid(pack_rep, pack_key, out_rep, member_key, keep):
    src_ev = os.path.join(pack_rep, pack_key + '_evid.json')
    dst_ev = os.path.join(out_rep, member_key + '_evid.json')
    if keep and os.path.exists(src_ev):
        shutil.copy2(src_ev, dst_ev)
    elif os.path.exists(dst_ev):
        try:
            os.remove(dst_ev)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser(description='將打包審核回覆拆回單段終審回覆')
    ap.add_argument('--pack', required=True, help='打包審核目錄（含 索引_pack.json 與 回覆/）')
    ap.add_argument('--out', required=True, help='拆回輸出目錄（會寫入 <out>/回覆/）')
    ap.add_argument('--clean', action='store_true', help='拆回前先清空 <out>/回覆')
    args = ap.parse_args()

    pack_dir = _resolve(args.pack)
    pack_rep = os.path.join(pack_dir, '回覆')
    out_dir = _resolve(args.out)
    out_rep = os.path.join(out_dir, '回覆')

    idx_path = os.path.join(pack_dir, '索引_pack.json')
    if not os.path.exists(idx_path):
        raise SystemExit('找不到索引檔：' + idx_path)
    mapping = json.load(io.open(idx_path, encoding='utf-8'))

    if args.clean and os.path.isdir(out_rep):
        shutil.rmtree(out_rep)
    os.makedirs(out_rep, exist_ok=True)

    st = {'packs_total': len(mapping), 'packs_audited': 0, 'packs_pending': 0,
          'packs_error': [], 'packs_fallback': [], 'units_total': 0,
          'units_pass': 0, 'units_fix': 0}

    for pack_key, members in mapping.items():
        if not members:
            continue
        rp = os.path.join(pack_rep, pack_key + '_回.txt')
        if not os.path.exists(rp):
            st['packs_pending'] += 1
            continue
        rt = io.open(rp, encoding='utf-8').read()
        vd = MI.verdict(rt)
        if vd == 'ERROR':
            st['packs_error'].append(pack_key)
            continue
        st['packs_audited'] += 1

        if len(members) == 1:
            mk = members[0]
            shutil.copy2(rp, os.path.join(out_rep, mk + '_回.txt'))
            _sync_evid(pack_rep, pack_key, out_rep, mk, keep=(vd == 'FIX'))
            st['units_total'] += 1
            if vd == 'FIX':
                st['units_fix'] += 1
            else:
                st['units_pass'] += 1
            continue

        if vd == 'PASS':
            for mk in members:
                _write_pass(os.path.join(out_rep, mk + '_回.txt'))
                _sync_evid(pack_rep, pack_key, out_rep, mk, keep=False)
                st['units_total'] += 1
                st['units_pass'] += 1
            continue

        fixes_txt = _fixes_block(rt)
        items = _split_fix_items(fixes_txt, len(members))
        if not items:
            st['packs_error'].append(pack_key)
            st['packs_audited'] -= 1
            continue

        per_member = {i: [] for i in range(1, len(members) + 1)}
        used_fallback = False
        for idxs, line in items:
            if idxs is None:
                used_fallback = True
                for i in per_member:
                    per_member[i].append(line)
            else:
                for i in idxs:
                    per_member[i].append(line)

        if used_fallback:
            st['packs_fallback'].append(pack_key)

        for i, mk in enumerate(members, 1):
            dst_rp = os.path.join(out_rep, mk + '_回.txt')
            st['units_total'] += 1
            if per_member[i]:
                _write_fix(dst_rp, per_member[i])
                _sync_evid(pack_rep, pack_key, out_rep, mk, keep=True)
                st['units_fix'] += 1
            else:
                _write_pass(dst_rp)
                _sync_evid(pack_rep, pack_key, out_rep, mk, keep=False)
                st['units_pass'] += 1

    print('已審 pack：%d／%d（待審 %d、異常 %d）'
          % (st['packs_audited'], st['packs_total'], st['packs_pending'], len(st['packs_error'])))
    print('拆回單位：%d（PASS：%d、FIX：%d、整包安全退路：%d）→ %s'
          % (st['units_total'], st['units_pass'], st['units_fix'],
             len(st['packs_fallback']), os.path.relpath(out_rep, B)))
    if st['packs_fallback']:
        print('  安全退路 pack：', st['packs_fallback'])
    if st['packs_error']:
        print('  ⚠ 異常 pack（未寫出，建議改名 _異常.txt 後補審）：', st['packs_error'])
        io.open(os.path.join(out_dir, '_異常pack清單.log'), 'w', encoding='utf-8').write('\n'.join(st['packs_error']) + '\n')


if __name__ == '__main__':
    main()
