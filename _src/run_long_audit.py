# -*- coding: utf-8 -*-
"""長段拼回後補走終審：建材料 → 審核 → 修訂 → 定稿。

用法： python -X utf8 _src/run_long_audit.py --book 業疏 [--audit-run]
"""
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PY = sys.executable
sys.path.insert(0, os.path.join(B, '_src'))
import book_config as BC  # noqa: E402

SRC_RE = re.compile(r'■ (疏文|記文|鈔文|律文|註文|序文)（原文）\s*\n+(.+?)(?=\n+■ |\n+【|\Z)', re.S)


def build(book):
    root = os.path.join(B, '測試', '重譯', book, '_長段')
    mp = os.path.join(root, '_對應.json')
    if not os.path.exists(mp):
        print(book, '無長段'); return None
    mapping = json.load(io.open(mp, encoding='utf-8'))
    groups = {}
    for m in mapping:
        groups.setdefault((m['chunk'], m['idx']), []).append(m)
    out = os.path.join(root, '_終審材料')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, '回覆'), exist_ok=True)
    cfg = BC.cfg(book)
    fin = os.path.join(root, '_定稿')
    n = 0
    for (chunk, idx), parts in sorted(groups.items()):
        parts.sort(key=lambda x: x['part'])
        origs, labs = [], []
        for p in parts:
            fp = os.path.join(root, '_材料', p['file'])
            if not os.path.exists(fp):
                continue
            t = io.open(fp, encoding='utf-8').read()
            for lab, body in SRC_RE.findall(t):
                labs.append(lab)
                origs.append(body.strip())
        fpath = os.path.join(fin, '%s_L%04d.txt' % (chunk, idx + 1))
        if not origs or not os.path.exists(fpath):
            continue
        key = '%s_L%04d' % (chunk, idx + 1)
        lab = labs[0] if labs else cfg['unit']
        _pre = _post = ''
        for p in (parts[0], parts[-1]):
            fp = os.path.join(root, '_材料', p['file'])
            if not os.path.exists(fp):
                continue
            _t = io.open(fp, encoding='utf-8').read()
            _m = re.search(r'【前文背景[^】]*】\s*\n+(.+?)(?=\n+【|\Z)', _t, re.S)
            if _m and not _pre:
                _pre = _m.group(1).strip()
            _m2 = re.search(r'【後文背景[^】]*】\s*\n+(.+?)(?=\n+【|\Z)', _t, re.S)
            if _m2:
                _post = _m2.group(1).strip()
        md = ['（出處：《%s》%s，第 %d 段）' % (book, chunk, idx + 1), '']
        if _pre:
            md += ['【前文背景（僅供參考，嚴禁譯入正文）】', '', _pre, '']
        md += ['【本次待審單元】', '', '■ %s（原文）' % lab, '', ''.join(origs), '']
        if _post:
            md += ['【後文背景（僅供參考，嚴禁譯入正文）】', '', _post, '']
        io.open(os.path.join(out, key + '.md'), 'w', encoding='utf-8').write('\n'.join(md))
        io.open(os.path.join(out, '回覆', key + '_回.txt'), 'w', encoding='utf-8').write(
            '## 1. 結論\n\nREVISED\n\n## 2. 分歧與裁決\n\n（長段拼回定稿，無裁決參考）\n\n'
            '## 3. 修正後的譯文\n\n【%s】\n%s\n'
            % (lab, __import__('re').sub(
                r'^\s*\**\s*【(?:疏文|記文|鈔文|律文|註文|序文)】\s*\**\s*', '',
                io.open(fpath, encoding='utf-8').read().strip())))
        n += 1
    print('%s：終審材料 %d 份 → %s' % (book, n, os.path.relpath(out, B)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True)
    ap.add_argument('--audit-run', action='store_true')
    args = ap.parse_args()
    out = build(args.book)
    if not out:
        return
    base = '測試/重譯/%s/_長段' % args.book
    subprocess.run([PY, '-X', 'utf8', '_src/mk_audit_materials.py',
                    '--src', base + '/_終審材料', '--out', base + '/_終審'],
                   cwd=B, check=True)
    if not args.audit_run:
        print('材料已備妥；加 --audit-run 直接跑審核')
        return
    env = dict(os.environ)
    env.update({'QWEN_SHUJI_SRC': ('重譯/%s/_長段/_終審' % args.book),
                'QWEN_LOCAL': '1', 'QWEN_NO_WEB': '0',
                'QWEN_MAX_SEARCH': '2', 'QWEN_MAX_FETCH': '1',
                'QWEN_RAW_SAVE': '1', 'QWEN_NO_CITE': '0',
                'QWEN_EFFORT': 'xhigh', 'QWEN_KEEP_THINKING': '1',
                'QWEN_400_FALLBACK': '1', 'QWEN_WORKERS': '20'})
    subprocess.run([PY, '-X', 'utf8', '_src/qwen_local.py'], cwd=B, env=env)
    subprocess.run([PY, '-X', 'utf8', '_src/mk_revise_materials.py',
                    '--r1', base + '/_終審材料', '--audit', base + '/_終審',
                    '--out', base + '/_終修'], cwd=B, check=True)
    env['QWEN_SHUJI_SRC'] = '重譯/%s/_長段/_終修' % args.book
    env['QWEN_NO_TOOLS'] = '1'
    env['QWEN_LOCAL'] = '0'
    env['QWEN_EFFORT'] = 'xhigh'
    subprocess.run([PY, '-X', 'utf8', '_src/qwen_local.py'], cwd=B, env=env)


if __name__ == '__main__':
    main()
