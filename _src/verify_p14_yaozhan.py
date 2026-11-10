# -*- coding: utf-8 -*-
"""會本_篇14 第 5 步（腰斬段重切）驗證。

比對：備份 `歸檔/會本_篇14_腰斬修正前/` vs 現行 docx／HTML／PDF。
輸出 PASS/FAIL 行，供 `verify.txt` 存檔。
"""
import io, os, re, json, html, collections, hashlib
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BK = os.path.join(B, '歸檔', '會本_篇14_腰斬修正前')
HB = os.path.join(B, '白話', '行事鈔資持記句級合編_卷中之二.docx')
HB0 = os.path.join(BK, '白話', '行事鈔資持記句級合編_卷中之二.docx')
YUAN = os.path.join(B, '白話', '會本_篇14_隨戒釋相.docx')
HTML = os.path.join(B, 'docs', 'hebian', '卷中之二.html')
PDF = os.path.join(B, '白話', 'PDF', '行事鈔資持記句級合編_卷中之二.pdf')

CASES = [
    (1, 'down', 10, 12, '四中。', '第四種用意中。'),
    (2, 'down', 29, 31, '名中。', '戒名中。'),
    (3, 'up', 33, 35, '具一，即受而不往。', '只具備一者，就是接受了委託卻還沒有前往交涉。'),
    (4, 'down', 74, 76, '制意中。', '在制戒意圖中：'),
    (5, 'down', 100, 102, '釋中，初文。', '解釋文中，第一段。'),
    (6, 'down', 103, 105, '二不定，標指中。', '第二部分不定法，標名指示中：'),
    (7, 'down', 109, 111, '初句標名。', '第一句標示名稱。'),
    (8, 'down', 215, 217, '戒名。', '戒名。'),
    (9, 'down', 219, 221, '釋中。', '在解釋中：'),
    (10, 'down', 225, 227, '戒名。', '戒名。'),
    (11, 'down', 247, 249, '緣中。', '在犯戒條件中。'),
    (12, 'up', 251, 253, '但緣在於毛，故制開外耳。',
     '只是因為制戒的因緣起於羊毛，所以才特別在羊毛之外作了開許與限制罷了。'),
    (13, 'up', 317, 319, '為利故出，強增價而高，曰賣也。',
     '為了謀取暴利而將物品出手，故意強行抬高價格索取暴利，這就叫做「賣」。'),
    (14, 'down', 333, 335,
     '列緣中。五綴者，律云：相去兩指間一綴〔中人一指面一寸，即取痕脈長二寸許，即為一綴；',
     '列出的犯戒條件中。五道補綴，律中說：相距兩指之間就算一道補綴〔普通人一指寬約一寸，也就是裂痕長約二寸左右，便算一道補綴；'),
    (15, 'up', 358, 360,
     '忽有急緣，不及夏竟，預先持施；佛開安居未竟，十日內受，故有二過，如緣所解。',
     '忽然有了緊急變故，來不及等到結夏圓滿，便預先拿來布施；佛陀開許在安居尚未結束前，'
     '十天之內可以接受，所以會產生兩種過失，如同犯戒條件所解釋的。'),
    (16, 'down', 371, 373, '戒名。', '戒名。'),
]


def idx(n):
    return 3 + 2 * (n - 1)


def main():
    out = []

    def rec(ok, label, detail=''):
        out.append(('PASS' if ok else 'FAIL') + '\t' + label + '\t' + str(detail))

    d = Document(HB)
    ps = [p.text for p in d.paragraphs]
    d0 = Document(HB0)
    qs = [p.text for p in d0.paragraphs]
    rec(len(ps) == 753, 'docx 段數 753', len(ps))
    rec(sum(len(x) for x in ps) == 183958, 'docx 字數 183958', sum(len(x) for x in ps))
    rec(collections.Counter(''.join(ps)) == collections.Counter(''.join(qs)),
        '字元多重集與備份相同', '')
    tags = [ps[i] for i in range(3, len(ps), 2)]
    rec(len(tags) == 375 and sum(1 for x in tags if x.startswith('【鈔】')) == 75
        and sum(1 for x in tags if x.startswith('【記】')) == 300,
        'docx 組數 375（鈔 75／記 300）', (len(tags),))

    ok_all = True
    for case, dirn, a, n, frag, frag_tr in CASES:
        pa, ta, pc, tc = ps[idx(a)], ps[idx(a) + 1], ps[idx(n)], ps[idx(n) + 1]
        if dirn == 'down':
            good = pc.startswith('【記】' + frag) and not pa.endswith(frag) \
                and tc.startswith(frag_tr)
        else:
            good = pa.endswith(frag) and not pc.startswith('【記】' + frag) \
                and ta.endswith(frag_tr)
        good = good and ps[idx(a) + 2].startswith('【鈔】') and idx(a) + 2 < idx(n)
        ok_all = ok_all and good
        rec(good, 's%d→s%d 重切正確（%s）' % (a, n, dirn), '')
    dup = []
    for s in ps:
        t = s[3:] if s[:3] in ('【記】', '【鈔】') else s
        if any(t[j:j + 50] == t[j + 1:j + 51] for j in range(len(t) - 51)):
            dup.append(t[:12])
    rec(not dup, '同段 ≥50 字重複 0', dup[:3])

    h = io.open(HTML, encoding='utf-8').read()
    pat = re.compile(r'<div class="pair" id="(s\d+)"><div class="(o2|o)">(.*?)</div>'
                     r'<div class="t">(.*?)</div></div>', re.S)
    hp = pat.findall(h)
    rec(len(hp) == 375, 'HTML 組數 375', len(hp))
    pairs = [(ps[i], ps[i + 1]) for i in range(3, len(ps) - 1, 2)]
    same = all(html.unescape(o) == p[0] and html.unescape(t) == p[1]
               for p, (sid, cls, o, t) in zip(pairs, hp))
    rec(same, 'HTML 與 docx 逐段相同', '')
    ok2 = all((html.unescape(hp[n - 1][2]).startswith('【記】' + frag) if dirn == 'down'
               else html.unescape(hp[a - 1][2]).endswith(frag))
              for case, dirn, a, n, frag, frag_tr in CASES)
    rec(ok2, 'HTML 16 處重切正確', '')

    try:
        from pypdf import PdfReader
        r = PdfReader(PDF)
        rec(len(r.pages) == 161, 'PDF 頁數 161', len(r.pages))
        t = ''.join((p.extract_text() or '') for p in r.pages).replace('\n', '').replace(' ', '')
        ok3 = all(frag in t for case, dirn, a, n, frag, frag_tr in CASES)
        rec(ok3, 'PDF 含 16 處重切文字', '')
        rec('第四種用意中。根本的淫欲業行' in t, 'PDF 譯文同步（s12）', '')
    except Exception as e:
        rec(False, 'PDF 檢查', repr(e))

    rec(os.path.getsize(YUAN) == os.path.getsize(os.path.join(BK, '白話', '會本_篇14_隨戒釋相.docx')),
        '會本_篇14_隨戒釋相.docx 未動', os.path.getsize(YUAN))

    txt = '\n'.join(out)
    print(txt)
    io.open(os.path.join(BK, 'verify.txt'), 'w', encoding='utf-8').write(txt + '\n')
    bad = [x for x in out if x.startswith('FAIL')]
    print('---- %d/%d PASS ----' % (len(out) - len(bad), len(out)))


if __name__ == '__main__':
    main()
