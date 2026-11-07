import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for book, vols in (('nicao', ['卷上', '卷中', '卷下']), ('yichao', ['卷上', '卷中']), ('yeshu', ['卷一', '卷二', '卷三', '卷四'])):
    for v in vols:
        h = io.open(B + r'\docs\%s\%s.html' % (book, v), encoding='utf-8').read()
        body = h[h.find('<main>'):]
        ps = re.findall(r'<div class="pair"[^>]*><div class="o">(.*?)</div>', body, re.S)
        bad = 0
        for o in ps:
            t = re.sub('<[^>]+>', '', o)
            if len(t) > 20 and not re.search(r'[，。、；：？！]', t):
                bad += 1
        rat = (100.0 * bad / len(ps)) if ps else 0
        print('%-8s %-4s pairs %4d 無標點 %3d (%.0f%%)' % (book, v, len(ps), bad, rat))
