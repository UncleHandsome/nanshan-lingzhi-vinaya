# -*- coding: utf-8 -*-
"""r2 1331+ 摘要器：抽出回應中的「必改」級意見，並就現行譯文定位引號片段。
用法: python _r2b_digest.py 1331 1332 ... → 寫出 _r2b_dg.txt
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

ROOT = L.ROOT
RESP = os.path.join(ROOT, 'batch_qwen', 'r2')
SEC = re.compile(r'^\s*#{0,4}\s*【(?:(\d{4})-)?(\d{4})】(.*)$')
Q = re.compile(r'「([^」]{1,80})」')
SEQREF = re.compile(r'【(\d{4})】')

HMAP = [('明確錯誤', 'FIX'), ('明顯誤譯', 'FIX'), ('必須改', 'FIX'), ('必改', 'FIX'),
        ('需改', 'FIX'), ('硬傷', 'FIX'), ('建議改', 'FIX'), ('應改', 'FIX'),
        ('增譯', 'POLISH'), ('語意偏移', 'WARN'), ('待查', 'WARN'), ('可商', 'WARN'),
        ('潤飾', 'POLISH'), ('建議調整', 'POLISH')]


def hdr(s):
    st = s.strip()
    if st.startswith('#'):
        t = st.lstrip('#').strip().strip('*').strip()
    elif st.startswith('**') and st.endswith('**'):
        t = st.strip('*').strip()
    else:
        return None
    if len(t) > 30:
        return None
    for k, v in HMAP:
        if k in t:
            return v
    return None


def load_resp(n):
    p = os.path.join(RESP, 'resp_%04d.txt' % n)
    if not os.path.exists(p):
        return None
    return open(p, encoding='utf-8-sig').read().replace('\r\n', '\n')


def bullets(text):
    out = []
    seq = None
    mode = None
    cur = None
    for line in text.split('\n'):
        m = SEC.match(line)
        if m:
            if cur:
                out.append(cur); cur = None
            seq = int(m.group(2))
            continue
        s = line.strip()
        if not s or s == '---':
            continue
        h = hdr(s)
        if h:
            if cur:
                out.append(cur); cur = None
            mode = h
            continue
        if re.match(r'^(?:[-*•]|\d+[.、]|\|)', s):
            if cur:
                out.append(cur)
            cur = [seq, s, mode]
        elif cur is not None:
            cur[1] += ' ' + s
        else:
            cur = [seq, s, mode]
            out.append(cur)
            cur = None
    if cur:
        out.append(cur)
    res = []
    res0 = []
    for seq, s, md in out:
        if '❌' in s or '必改' in s or '★' in s:
            k = 'FIX'
        elif '⚠' in s:
            k = 'WARN'
        elif '✏' in s or '○' in s:
            k = 'POLISH'
        elif '✔' in s or '✅' in s:
            k = 'OK'
        elif s.startswith('|'):
            k = 'TABLE'
        else:
            k = md or 'NOTE'
        if k == 'NOTE':
            m2 = SEQREF.search(s)
            if m2 and ('→' in s or '建議' in s):
                k = 'FIX'
                if seq is None:
                    seq = int(m2.group(1))
        res.append((seq, k, s))
    return res


def main():
    ns = [int(a) for a in sys.argv[1:] if a.isdigit()]
    cache = {}
    lines = []
    meta = {}
    for n in ns:
        t = load_resp(n)
        if t is None:
            lines.append('##### resp_%d MISSING\n' % n)
            continue
        recs = L.parse_review(n)
        if not recs:
            lines.append('##### %d: 校閱材料缺\n' % n)
            continue
        segs = {}
        for r in recs:
            key = (r['book'], r['chunk'])
            if key not in cache:
                cache[key] = L.Out(*key)
            o = cache[key]
            segs[r['seq']] = (r['book'], r['chunk'], r['seg'], o, r['trans'])
        bs = bullets(t)
        cnt = dict(FIX=0, WARN=0, POLISH=0, OK=0, TABLE=0, NOTE=0)
        for seq, k, s in bs:
            cnt[k] = cnt.get(k, 0) + 1
        meta[n] = cnt
        lines.append('##### resp_%d  segs=%d  FIX=%d WARN=%d POLISH=%d OK=%d NOTE=%d' % (
            n, len(recs), cnt['FIX'], cnt['WARN'], cnt['POLISH'], cnt['OK'], cnt['NOTE']))
        for seq, k, s in bs:
            if k != 'FIX':
                continue
            s = re.sub(r'\s+', ' ', s)
            lines.append('[%d-%04d] %s' % (n, seq or 0, s[:380]))
            info = segs.get(seq)
            if not info:
                lines.append('    <no seg %s>' % seq)
                continue
            book, chunk, sg, o, mat = info
            cur = o.segs[sg - 1] if sg - 1 < len(o.segs) else ''
            stale = '' if (mat or '').replace('\n', '') == (cur or '').replace('\n', '') else ' MAT!=CUR'
            lines.append('    [%s/%s#%d%s]' % (book, chunk, sg, stale))
            frags = [f.replace('**', '') for f in Q.findall(s)]
            hit = False
            for f in frags:
                i = cur.find(f)
                if i >= 0:
                    hit = True
                    a = max(0, i - 55); b = min(len(cur), i + len(f) + 55)
                    lines.append('    ...%s...' % cur[a:b])
                    break
            if not hit:
                lines.append('    <frag not in cur> cur=' + cur[:140])
        lines.append('')
    out = os.path.join(ROOT, 'AI語譯', '_work', 'review', '_r2b_dg.txt')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines))
    tm = os.path.join(ROOT, 'AI語譯', '_work', 'review', '_r2b_meta.json')
    old = {}
    if os.path.exists(tm):
        old = json.load(open(tm, encoding='utf-8'))
    old.update({str(k): v for k, v in meta.items()})
    json.dump(old, open(tm, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('wrote', out, len(lines))


if __name__ == '__main__':
    main()
