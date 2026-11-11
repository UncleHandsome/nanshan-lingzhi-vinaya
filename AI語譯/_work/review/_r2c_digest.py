# -*- coding: utf-8 -*-
"""把 resp_13xx/14xx 壓成可讀清單：抓「段落標題」與「建議/必改」類句子，長文截斷。
用法: python _r2c_digest.py 1342 1343 ...  -> _r2c_dg.txt
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2c_lib as L

SEC = re.compile(r'【(\d{4})-(\d{4})】')
NUM = re.compile(r'^\s*(?:#{1,4}\s*)?(?:\*\*)?#?(\d{4})-(\d{4})')
BULL = re.compile(r'^\s*(?:[-*•·]|\d+[.、)]|#\d+|[①②③④⑤⑥⑦⑧⑨⑩⑪⑫]|❌|★|✔|✅|（\d+）)')
ACT = re.compile(r'必改|建議|宜作|宜改|宜譯|應改|應作|改為|改作|修正|錯誤|誤解|誤譯|譯錯|漏譯|增譯|不符|刪去|補|★|❌|不通|矛盾|相反|顛倒|失')


def squeeze(s, lim=260):
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= lim else s[:lim] + '…'


def main():
    ns = [int(a) for a in sys.argv[1:] if a.isdigit()]
    out = []
    for n in ns:
        p = os.path.join(L.RESP, 'resp_%04d.txt' % n)
        if not os.path.exists(p):
            out.append('##### resp_%d MISSING\n' % n)
            continue
        t = open(p, encoding='utf-8-sig').read().replace('\r\n', '\n')
        out.append('##### resp_%d  (%d chars)' % (n, len(t)))
        cur = None
        kept = 0
        for line in t.split('\n'):
            s = line.rstrip()
            if not s.strip() or s.strip() == '---':
                continue
            if SEC.search(s) or re.match(r'^\s*#{1,4}\s', s) or s.strip().startswith('**'):
                out.append(s.strip()[:200])
                cur = s.strip()[:200]
                continue
            if BULL.match(s):
                if ACT.search(s):
                    out.append('  ' + squeeze(s))
                    kept += 1
                continue
            # 續行併入上一條
            if out and out[-1].startswith('  ') and ACT.search(s):
                out[-1] = out[-1] + ' ' + squeeze(s, 120)
        out.append('  <kept %d bullets>' % kept)
        out.append('')
    dst = os.path.join(os.path.dirname(__file__), '_r2c_dg.txt')
    open(dst, 'w', encoding='utf-8').write('\n'.join(out))
    print('wrote', dst, len(out), 'lines')


if __name__ == '__main__':
    main()
