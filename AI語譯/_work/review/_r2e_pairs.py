# -*- coding: utf-8 -*-
"""r2 意見配對抽取：把 resp 壓成 (段號, 引文, 建議) 清單。
用法: python _r2e_pairs.py 1664 [...]
"""
import os, sys, io, re
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

RESP = os.path.join(L.ROOT, 'batch_qwen', 'r2')
SEGREF = re.compile(r'(?:#\s*(\d{1,4})|【\s*#?(\d{1,4})\s*】|(?<![0-9])(\d{4})(?![0-9]))')
Q = re.compile(r'「([^」]{1,80})」')


def main():
    for a in [x for x in sys.argv[1:] if not x.startswith('--')]:
        n = int(a)
        rp = os.path.join(RESP, 'resp_%d.txt' % n)
        print('##### %d #####' % n)
        if not os.path.exists(rp):
            print('MISSING')
            continue
        txt = open(rp, encoding='utf-8').read()
        cur = '?'
        out = []
        for ln in txt.splitlines():
            m = SEGREF.search(ln)
            if m:
                cur = next(g for g in m.groups() if g)
            if '無問題' in ln or '沒問題' in ln:
                cur = '?'
                continue
            qs = Q.findall(ln)
            if not qs:
                continue
            arrow = '→' in ln
            if arrow:
                pre, post = ln.split('→', 1)
                qpre = Q.findall(pre)
                qpost = Q.findall(post)
                if qpre and qpost:
                    out.append('#%s 「%s」→「%s」' % (cur, qpre[-1], qpost[0]))
                    continue
            # otherwise print quotes + tail
            tail = ln.strip()
            tail = re.sub(r'\*\*|__|`', '', tail)
            if len(tail) > 150:
                tail = tail[:150] + '…'
            out.append('#%s %s' % (cur, tail))
        seen = set()
        for x in out:
            if x in seen:
                continue
            seen.add(x)
            print(x)


if __name__ == '__main__':
    main()
