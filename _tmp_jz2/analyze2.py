# -*- coding: utf-8 -*-
"""卷中之二 鈔記序列分析 v2"""
import io, re, json, collections
from docx import Document

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
K2, K3 = 904, 1656


def load_pairs():
    ps = [x.text for x in Document(B + r"\白話\會本_篇14_隨戒釋相.docx").paragraphs]
    seg = ps[K2:K3]
    rows = []
    i = 0
    while i < len(seg):
        t = seg[i]
        m = re.match(r'^【(鈔|記)(\d+)】(（[^）]*）)?', t)
        if m:
            rows.append(dict(kind=m.group(1), num=int(m.group(2)),
                             sub=(m.group(3) or ''), body=t[m.end():],
                             tr=seg[i + 1] if i + 1 < len(seg) else '',
                             pos=K2 + i, idx=len(rows)))
            i += 2
        else:
            i += 1
    return rows


UNIT = [
    ('僧殘1 故失精戒', '僧殘篇中，故失精戒第一'),
    ('僧殘2 摩觸女人戒', '摩觸女人戒第二'),
    ('僧殘3 與女人麁語戒', '與女人麁語戒第三'),
    ('僧殘4 向女歎身索供戒', '向女歎身索供戒第四'),
    ('僧殘5 媒人戒', '媒人戒第五'),
    ('僧殘6 無主僧不處分過量房戒', '無主僧不處分過量房戒第六'),
    ('僧殘7 有主僧不處分房戒', '有主僧不處分房戒第七'),
    ('僧殘8 無根重罪謗他戒', '無根重罪謗他戒第八'),
    ('僧殘9 假根謗戒', '假根謗戒第九'),
    ('僧殘10 破僧違諫戒', '破僧違諫戒第十'),
    ('僧殘11 助破僧違諫戒', '助破僧違諫戒第十一'),
    ('僧殘12 污家擯謗違僧諫戒', '污家擯謗違僧諫戒第十二'),
    ('僧殘13 惡性拒僧違諫戒', '惡性拒僧違諫戒第十三'),
    ('二不定總科', '二不定中，文疏久列'),
    ('不定1 初不定', '初不定中，四緣犯之'),
    ('不定2 後不定', '後不定戒，略同前者'),
    ('三十捨墮總科', '三十捨墮，懺法如後'),
    ('捨墮1 長衣過限戒', '初長衣過限戒'),
    ('捨墮2 離三衣宿戒', '離三衣宿戒第二'),
    ('捨墮3 月望衣戒', '月望衣戒三'),
    ('捨墮4 取非親尼衣戒', '取非親尼衣戒四'),
    ('捨墮5 使非親尼浣故衣戒', '使非親尼浣故衣戒五'),
    ('捨墮6 從非親俗人乞衣戒', '從非親俗人乞衣戒六'),
    ('捨墮7 過分取衣戒', '過分取衣戒七'),
    ('捨墮8 勸增衣價戒', '勸增衣價戒八'),
    ('捨墮9 勸二家增衣價戒', '勸二家增衣價戒九'),
    ('捨墮10 過限急索衣價戒', '過限怱切索衣價戒十'),
    ('捨墮11 乞蠶綿作袈裟戒', '乞蠶綿作袈裟戒十一'),
    ('捨墮12 黑毛臥具戒', '黑毛臥具戒十二'),
    ('捨墮13 白毛三衣戒', '白毛三衣戒十三'),
    ('捨墮14 減六年作三衣戒', '減六年作三衣戒十四'),
    ('捨墮15 不貼坐具戒', '不貼坐具戒十五'),
    ('捨墮16 持羊毛過限戒', '持羊毛過限戒十六'),
    ('捨墮17 使非親尼浣染毛戒', '使非親尼浣染毛戒十七'),
    ('捨墮18 畜錢寶戒', '畜錢寶戒十八'),
    ('捨墮19 貿寶戒', '貿寶戒十九'),
    ('捨墮20 販賣戒', '販賣戒二十'),
    ('捨墮21 畜長鉢過限戒', '畜長鉢過限戒二十一'),
    ('捨墮22 乞鉢戒', '乞鉢戒二十二'),
    ('捨墮23 自乞縷使非親織戒', '自乞縷使非親織戒二十三'),
    ('捨墮24 勸織師增衣縷戒', '勸織師增衣縷戒二十四'),
    ('捨墮25 奪衣戒', '奪衣戒二十五'),
    ('捨墮26 畜七日藥過限戒', '畜七日藥過限戒二十六'),
    ('捨墮27 過前求雨衣過前用戒', '過前求雨衣過前用戒二十七'),
    ('捨墮28 過前受急施衣過後畜戒', '過前受急施衣過後畜戒二十八'),
    ('捨墮29 有難蘭若離衣戒', '有難蘭若離衣戒二十九'),
    ('捨墮30 說迴僧物入己戒', '說迴僧物入'),
]
# 記錨點：(單元序 1-47, 記號, sub, 段內位置, 說明)
A = [
    (1, 377, '', 16, '第一戒。'),
    (2, 385, '', 9, '第二。'),
    (3, 398, '', 81, '第三。'),
    (4, 402, '', 88, '第四。'),
    (5, 405, '', 33, '第五。'),
    (6, 412, '', 77, '第六。'),
    (7, 439, '', 10, '第七。'),
    (8, 441, '', 60, '第八。'),
    (9, 446, '', 109, '第九。'),
    (10, 448, '', 96, '第十。'),
    (11, 453, '（後半）', 0, '十一。'),
    (12, 454, '', 85, '十二。'),
    (13, 461, '', 30, '十三。'),
    (14, 463, '', None, '二不定，標指中'),
    (15, 465, '', None, '一屏處不定。'),
    (16, 467, '', None, '二露處不定。'),
    (17, 468, '', None, '三十捨墮，名兼罪懺'),
    (18, 468, '', None, '初戒。〔佛在舍衛'),
    (19, 487, '（後半）', 0, '第二。'),
    (20, 524, '', 25, '第三。'),
    (21, 527, '', 23, '第四。'),
    (22, 532, '', 67, '第五。'),
    (23, 537, '', 0, '第六。'),
    (24, 543, '', 78, '第七。'),
    (25, 546, '', 43, '第八。'),
    (26, 549, '', 0, '第九。'),
    (27, 550, '', 74, '第十。'),
    (28, 553, '', 28, '十一。'),
    (29, 563, '', 16, '十二。'),
    (30, 564, '', 83, '十三。'),
    (31, 566, '', 33, '十四。'),
    (32, 567, '', 93, '十五。'),
    (33, 570, '', 59, '十六。'),
    (34, 573, '', 31, '十七。'),
    (35, 574, '', 47, '十八。'),
    (36, 622, '', 93, '十九。'),
    (37, 626, '', 36, '二十。'),
    (38, 639, '', 63, '二十一。'),
    (39, 640, '', 63, '二十二。'),
    (40, 642, '', 28, '二十三。'),
    (41, 644, '', 56, '二十四。'),
    (42, 646, '', 0, '二十五。'),
    (43, 648, '（後半）', 0, '二十六。'),
    (44, 651, '（後半）', 0, '二十七。'),
    (45, 657, '', 65, '二十八。'),
    (46, 662, '', 0, '二十九。'),
    (47, 668, '', 119, '三十。'),
]


def units_of(rows):
    # 鈔
    cur = None
    for r in rows:
        if r['kind'] == '鈔':
            hit = None
            for i, (name, pre) in enumerate(UNIT, 1):
                if r['body'].startswith(pre):
                    hit = i
                    break
            if hit:
                cur = hit
            r['u'] = cur
    # 記：先定錨點所在段序
    idx_of = {}
    for i, r in enumerate(rows):
        idx_of[(r['kind'], r['num'], r['sub'])] = i
    anchors = []
    for (u, num, sub, pos, txt) in A:
        i = idx_of.get(('記', num, sub))
        if i is None:
            raise SystemExit('找不到錨點段 記%d%s' % (num, sub))
        body = rows[i]['body']
        p = body.find(txt)
        if p < 0:
            raise SystemExit('錨文字不在 記%d%s：%s' % (num, sub, txt))
        if pos is None:
            pos = p
        elif p != pos:
            raise SystemExit('錨點位置不符 記%d%s：表%s 實%s %r' % (num, sub, pos, p, txt))
        anchors.append((u, i, pos, txt))
    # 排序檢查
    for k in range(1, len(anchors)):
        assert (anchors[k][1], anchors[k][2]) > (anchors[k - 1][1], anchors[k - 1][2]), anchors[k]
    # 每段歸屬
    for i, r in enumerate(rows):
        if r['kind'] != '記':
            continue
        u = 1
        for (au, ai, apos, txt) in anchors:
            if ai < i or (ai == i and apos == 0):
                u = au
            else:
                break
        r['u'] = u
    return rows, anchors


def main():
    rows = load_pairs()
    rows, anchors = units_of(rows)
    assert len(rows) == 376
    out = io.open(B + r"\_tmp_jz2\seq.txt", "w", encoding="utf-8")
    for i, r in enumerate(rows):
        out.write('%3d\t%s%03d%s\tU%02d\t%s\t%s\n' % (
            i, r['kind'], r['num'], r['sub'], r['u'], UNIT[r['u'] - 1][0], r['body'][:30]))
    out.close()
    # 各單元鈔段/記段位置
    print('單元\t鈔段序\t記段序')
    report = io.open(B + r"\_tmp_jz2\units.txt", "w", encoding="utf-8")
    leaks = []
    for u in range(1, len(UNIT) + 1):
        cs = [i for i, r in enumerate(rows) if r['kind'] == '鈔' and r['u'] == u]
        js = [i for i, r in enumerate(rows) if r['kind'] == '記' and r['u'] == u]
        report.write('U%02d %s\n  鈔 %s\n  記 %s\n' % (u, UNIT[u - 1][0], cs, js))
        if cs and js:
            # 錯位：記段位置 > 下一單元首鈔位置
            nxt = [i for i, r in enumerate(rows) if r['kind'] == '鈔' and r['u'] == u + 1]
            if nxt:
                bad = [j for j in js if j > nxt[0]]
                if bad:
                    leaks.append((u, bad, UNIT[u - 1][0]))
    report.close()
    print('錯位單元', len(leaks))
    for u, bad, name in leaks:
        print('  U%02d %s 記段排到下一戒鈔後：%s' % (u, name, [(rows[j]['num'], rows[j]['sub']) for j in bad]))
    print('單元數', len(UNIT))


if __name__ == '__main__':
    main()
