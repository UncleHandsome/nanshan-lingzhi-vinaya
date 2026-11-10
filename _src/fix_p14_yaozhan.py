# -*- coding: utf-8 -*-
"""會本_篇14 第 5 步：腰斬段重切（卷中之二）。

依 `腰斬段材料.md` 列出的 16 處（甲 6、乙 10），把被鈔文切斷的句子整句
歸到前段或後段，原文與譯文同步搬移；只搬不改字，段數、字數皆不變。
丙類 s106、s196 經判斷為「科文＋鈔（本宗文）」的正常結構，保留原狀。

判斷原則
--------
* 乙類（科判標目）：標目（「四中。」「名中。」「制意中。」…）緊接其解釋，
  解釋在鈔後，故整句下移到後段首（direction='down'）。
* 甲類：句子的後半在後段，若該句／該組並列屬於前段已開始的科段，則整句
  上移回前段（direction='up'）；若該組並列是對鈔文的逐句註解，則整組下移
  到後段（direction='down'）。

用法：
    python _src/fix_p14_yaozhan.py --dry-run
    python _src/fix_p14_yaozhan.py --apply
"""
import io, os, re, sys, json
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HB = os.path.join(B, '白話', '行事鈔資持記句級合編_卷中之二.docx')
LOG = os.path.join(B, '歸檔', '會本_篇14_腰斬修正前', 'changes.json')

# (case, 型, direction, 前段 s, 後段 s, 搬移原文, 搬移譯文, 依據)
CASES = [
    (1, '乙', 'down', 10, 12,
     '四中。', '第四種用意中。',
     '「四中。」為制意六種第四之科文，其釋「根本淫業即大惡源」在鈔後'),
    (2, '乙', 'down', 29, 31,
     '名中。', '戒名中。',
     '「名中。」為戒名科文，其釋「境過一一須分」在鈔後'),
    (3, '甲', 'up', 33, 35,
     '具一，即受而不往。', '只具備一者，就是接受了委託卻還沒有前往交涉。',
     '具三→具二→具一為釋第六文五節之第一節，具三、具二已在前段'),
    (4, '乙', 'down', 74, 76,
     '制意中。', '在制戒意圖中：',
     '「制意中。」為科文，其釋「初護自行者，淨口業故」在鈔後'),
    (5, '乙', 'down', 100, 102,
     '釋中，初文。', '解釋文中，第一段。',
     '「釋中，初文」之釋「旁略教者，即拘留孫偈」在鈔後'),
    (6, '乙', 'down', 103, 105,
     '二不定，標指中。', '第二部分不定法，標名指示中：',
     '「二不定，標指中」之釋「屏露不同為二…」在鈔後'),
    (7, '甲', 'down', 109, 111,
     '初句標名。', '第一句標示名稱。',
     '「初句標名」與「次句指同」為一對，皆註鈔文兩句，應同在鈔後'),
    (8, '乙', 'down', 215, 217,
     '戒名。', '戒名。',
     '「戒名。」之釋「失三受二…故名過分」在鈔後'),
    (9, '乙', 'down', 219, 221,
     '釋中。', '在解釋中：',
     '「釋中。」之釋「十六分之一者…」在鈔後'),
    (10, '乙', 'down', 225, 227,
     '戒名。', '戒名。',
     '「戒名。」之釋「越三語六默名過限…」在鈔後'),
    (11, '乙', 'down', 247, 249,
     '緣中。', '在犯戒條件中。',
     '「緣中。」之釋「先有故者，準此無故即應不犯」在鈔後'),
    (12, '甲', 'up', 251, 253,
     '但緣在於毛，故制開外耳。',
     '只是因為制戒的因緣起於羊毛，所以才特別在羊毛之外作了開許與限制罷了。',
     '「疏云：今若生譏…」句末「；」截斷，下接「但緣在於毛…」收句，應留前段'),
    (13, '甲', 'up', 317, 319,
     '為利故出，強增價而高，曰賣也。',
     '為了謀取暴利而將物品出手，故意強行抬高價格索取暴利，這就叫做「賣」。',
     '「準疏分三：販→買→賣」三項並列，販、買已在前段，賣應歸前段'),
    (14, '甲', 'down', 333, 335,
     '列緣中。五綴者，律云：相去兩指間一綴〔中人一指面一寸，即取痕脈長二寸許，即為一綴；',
     '列出的犯戒條件中。五道補綴，律中說：相距兩指之間就算一道補綴〔普通人一指寬約一寸，也就是裂痕長約二寸左右，便算一道補綴；',
     '「列緣中」科文及其「五綴者」句、夾註前半在鈔前，夾註後半在鈔後；'
     '科文之釋全在鈔後，故連科文一併下移，使夾註〔…〕完整'),
    (15, '甲', 'up', 358, 360,
     '忽有急緣，不及夏竟，預先持施；佛開安居未竟，十日內受，故有二過，如緣所解。',
     '忽然有了緊急變故，來不及等到結夏圓滿，便預先拿來布施；佛陀開許在安居尚未結束前，十天之內可以接受，所以會產生兩種過失，如同犯戒條件所解釋的。',
     '「戒名中。施主本為安居故施；」句末「；」截斷，下接「忽有急緣…」收句，應留前段'),
    (16, '乙', 'down', 371, 373,
     '戒名。', '戒名。',
     '「戒名。」之釋「疏云：許僧物者…」在鈔後'),
]

CHANGES = []


def idx(n):
    return 3 + 2 * (n - 1)


def run(apply):
    d = Document(HB)
    ps = d.paragraphs
    assert len(ps) == 753, len(ps)
    before_total = sum(len(p.text) for p in ps)
    assert before_total == 183958, before_total

    for case, typ, direction, a, c, frag, frag_tr, basis in CASES:
        pa, ta = ps[idx(a)], ps[idx(a) + 1]
        pc, tc = ps[idx(c)], ps[idx(c) + 1]
        assert len(pa.runs) == len(ta.runs) == len(pc.runs) == len(tc.runs) == 1, case
        A, AT, C, CT = pa.text, ta.text, pc.text, tc.text
        assert A.startswith('【記】') and C.startswith('【記】'), case
        old = (A, AT, C, CT)

        if direction == 'down':
            assert A.endswith(frag), (case, repr(A[-50:]))
            assert AT.endswith(frag_tr), (case, repr(AT[-50:]))
            nA, nAT = A[:-len(frag)], AT[:-len(frag_tr)]
            nC, nCT = '【記】' + frag + C[3:], frag_tr + CT
        else:
            assert C.startswith('【記】' + frag), (case, repr(C[:60]))
            assert CT.startswith(frag_tr), (case, repr(CT[:60]))
            nC, nCT = '【記】' + C[3 + len(frag):], CT[len(frag_tr):]
            nA, nAT = A + frag, AT + frag_tr

        # 只搬不改字：兩段合計字數不變、字元多重集不變
        assert len(nA) + len(nC) == len(A) + len(C), case
        assert len(nAT) + len(nCT) == len(AT) + len(CT), case
        assert sorted(nA + nC) == sorted(A + C), case
        assert sorted(nAT + nCT) == sorted(AT + CT), case
        assert nA.startswith('【記】') and nC.startswith('【記】') and len(nA) > 3 and len(nC) > 3

        if apply:
            pa.runs[0].text = nA
            ta.runs[0].text = nAT
            pc.runs[0].text = nC
            tc.runs[0].text = nCT

        CHANGES.append(dict(
            case=case, typ=typ, direction=direction, prev=a, chao=None, next=c,
            frag=frag, frag_tr=frag_tr, basis=basis,
            before=dict(prev=old[0], prev_tr=old[1], next=old[2], next_tr=old[3]),
            after=dict(prev=nA, prev_tr=nAT, next=nC, next_tr=nCT)))

    after_total = sum(len(p.text) for p in ps)
    assert after_total == before_total, (after_total, before_total)
    if apply:
        d.save(HB)
    print('%s：%d 處；段數 %d；字數 %d→%d' % (
        '已套用' if apply else 'dry-run', len(CASES), len(ps), before_total, after_total))
    for ch in CHANGES:
        print('[%2d]%s %s s%d→s%d  %s' % (
            ch['case'], ch['typ'], ch['direction'], ch['prev'], ch['next'], ch['frag'][:24]))
    if apply:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        json.dump(CHANGES, io.open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    if not apply and '--dry-run' not in sys.argv:
        raise SystemExit('請加 --dry-run 或 --apply')
    run(apply)
