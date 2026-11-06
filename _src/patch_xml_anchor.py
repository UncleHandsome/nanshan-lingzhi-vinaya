import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_xml_huiben.py'
s = io.open(p, encoding='utf-8').read()
old = """    anchors = []
    cur = 0
    for k, (o, t) in enumerate(zt):
        h = han(o)
        probe = h[:10]
        pos = H.find(probe, cur) if probe else -1
        if pos < 0:
            probe = h[:6]
            pos = H.find(probe, cur) if probe else -1
        if pos >= 0:
            cur = pos
            anchors.append(pos2p[pos])
        else:
            anchors.append(pos2p[cur] if cur < len(pos2p) else 0)"""
new = """    anchors = []
    cur = 0
    for k, (o, t) in enumerate(zt):
        h = han(o)[:80]
        best = None
        for L in (8, 7, 6, 5):
            for i in range(0, max(1, len(h) - L + 1)):
                seg = h[i:i + L]
                if len(set(seg)) < 3:
                    continue
                pos = H.find(seg, cur)
                if pos >= 0 and (best is None or pos < best):
                    best = pos
            if best is not None:
                break
        if best is not None:
            cur = best
            anchors.append(pos2p[best])
        else:
            anchors.append(anchors[-1] if anchors else 0)"""
if old in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('anchors v2')
else:
    print('missing')
