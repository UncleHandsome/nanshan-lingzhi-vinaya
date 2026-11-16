# -*- coding: utf-8 -*-
"""混合切法：舊組原樣保留（沿用既有新譯），只把舊組沒覆蓋的段另建新組。

輸出：_材料_hy（材料）＋ _hy_盲翻/回覆（可沿用者已預填）
"""
import io
import os
import re
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, '測試')
sys.path.insert(0, os.path.join(B, '_src'))
import mk_review_materials as M  # noqa: E402

BLOCK = re.compile(r'■ (疏文|記文|鈔文|律文|註文|序文)（原文）\s*\n+(.+?)(?=\n+■ |\n+【後文背景|\Z)', re.S)
PROV = re.compile(r'（出處：(?:《[^》]+》)?([^，]+)，第 (\d+)(?:–(\d+))? 段')
BOOKS = ['業疏', '戒疏', '尼鈔', '行事鈔', '義鈔', '資持記']


def norm(s):
    s = re.sub(r'【[疏記鈔律註序]】', '', s)
    s = re.sub(r'\[\s*\d+\s*\]', '', s)
    return re.sub(r'[\s　]', '', s)


def locate(a, body, start):
    nb = norm(body)
    for i in range(start, len(a)):
        na = norm(a[i])
        if na == nb:
            return i
    return None


def main():
    tot = [0, 0, 0]
    for bk in BOOKS:
        spec = M.BOOKS[bk]
        d = os.path.join(T, '重譯', bk, '_材料')
        rep = os.path.join(T, '重譯', bk, '_盲翻_對齊', '回覆')
        if not os.path.isdir(rep):
            rep = os.path.join(T, '重譯', bk, '_盲翻', '回覆')
        segs, covered = {}, {}
        old = []
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if not f.endswith('.md'):
                    continue
                t = io.open(os.path.join(d, f), encoding='utf-8').read()
                m = PROV.search(t)
                if not m:
                    continue
                ch = m.group(1).strip()
                if ch not in segs:
                    got = M.load_pair(spec, ch)
                    segs[ch] = got[0] if got else []
                a = segs[ch]
                body = ''.join(norm(b) for _, b in BLOCK.findall(t))
                idx = []
                bodies = [norm(b) for _, b in BLOCK.findall(t)]
                _bodies = set(norm(b) for _, b in BLOCK.findall(t))
                for k, seg in enumerate(a):
                    ns = norm(seg)
                    if ns and ns in _bodies:
                        idx.append(k)
                key = f[:-3]
                rp = os.path.join(rep, key + '_回.txt')
                old.append(dict(chunk=ch, idx=idx, key=key,
                                reply=io.open(rp, encoding='utf-8').read() if os.path.exists(rp) else None))
                for k in idx:
                    covered.setdefault(ch, set()).add(k)

        groups = M.build_groups(spec)
        new = []
        for g in groups:
            idx = list(range(g['s0'], g['s1'])) + list(range(g['g0'], g['g1']))
            cv = covered.get(g['chunk'], set())
            if idx and all(k in cv for k in idx):
                continue
            new.append(g)

        out = os.path.join(T, '重譯', bk, '_材料_hy')
        blind = os.path.join(T, '重譯', bk, '_hy_盲翻')
        for p in (out, blind):
            if os.path.isdir(p):
                shutil.rmtree(p)
        os.makedirs(out, exist_ok=True)
        os.makedirs(os.path.join(blind, '回覆'), exist_ok=True)

        # 新組
        for n, g in enumerate(new, 1):
            key = 'n%04d_%s_%04d' % (n, g['chunk'], g['s0'] + 1)
            _p = M.emit(g, 6, 4, out, n, book=bk)
            try:
                os.rename(_p, os.path.join(out, key + '.md'))
                _j2 = _p[:-3] + '.json'
                if os.path.exists(_j2):
                    os.rename(_j2, os.path.join(out, key + '.json'))
            except Exception:
                pass
        # 舊組：原樣複製材料與回覆
        have_reply = 0
        for o in old:
            if not o['idx']:
                continue
            src = os.path.join(d, o['key'] + '.md')
            if not os.path.exists(src):
                continue
            shutil.copy2(src, os.path.join(out, o['key'] + '.md'))
            _j = os.path.join(d, o['key'] + '.json')
            if os.path.exists(_j):
                shutil.copy2(_j, os.path.join(out, o['key'] + '.json'))
            if o['reply']:
                io.open(os.path.join(blind, '回覆', o['key'] + '_回.txt'), 'w',
                        encoding='utf-8').write(o['reply'])
                _u = os.path.join(rep, o['key'] + '_usage.json')
                if os.path.exists(_u):
                    shutil.copy2(_u, os.path.join(blind, '回覆', o['key'] + '_usage.json'))
                have_reply += 1
        need = len(new)
        tot[0] += len(old)
        tot[1] += need
        tot[2] += len(old) - have_reply
        print('%-4s 舊組 %5d（有回覆 %5d）｜新組 %5d｜總 %5d'
              % (bk, len(old), have_reply, need, len(old) + need))
    print('合計 舊 %d｜新 %d｜舊組缺回覆 %d' % (tot[0], tot[1], tot[2]))


if __name__ == '__main__':
    main()
