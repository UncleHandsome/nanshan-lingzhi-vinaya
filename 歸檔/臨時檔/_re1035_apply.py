# -*- coding: utf-8 -*-
"""套用第 3／5 輪真錯修正（001 檔）。備份 → 改 out → 出 fix_re10_35.tsv。"""
import io, os, json, shutil, hashlib

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out', '01_行事鈔')
REVIEW = os.path.join(B, 'AI語譯', '_work', 'review')
BAK = os.path.join(B, '歸檔', 're10_35修正前', '01_行事鈔')

# (chunk, seg, old, new, 條號, 理由)
EDITS = [
    # ---- 00_卷首 ----
    ('00_卷首', 41, '凡所制定的，都含有特殊的對治方便。',
     '凡所制定的，都含有異於外道法式的用意。', 1, '異術＝外道（記：異術即外道）'),
    ('00_卷首', 41, '就會讓外道藉此致其餘的言論。',
     '就會招致外道生起譏嫌非議。', 2, '致餘言＝招致譏謗（記：外道譏言…勿令外道以致餘言）'),
    ('00_卷首', 41, '第三，是為了對治不同宗派而來的問題。',
     '第三，是為了對辨其他宗派，教法才由此興起。', 3, '故來＝教由此而來（記：毘尼之教，因茲而制，故云來也）'),
    ('00_卷首', 44, '這豈不是為了保存在俗的教化，恐怕人墜入枉曲的坑陷？',
     '這豈不是為了顧存對世俗的化導，唯恐世人因譏謗而墮入邪道苦坑？', 4, '存化俗＝護俗化導；枉坑＝起謗墮邪道苦坑（記）'),
    ('00_卷首', 6, '前代修行的人是依託律藏',
     '前代諸師（律師）是依託律藏', 22, '前修即指前代諸師（記）'),
    ('00_卷首', 6, '致使辨析時產生矛盾乖戾，輕重的判定加倍分歧',
     '致使辨析罪過時，輕重的判定加倍分歧', 8, '釁戾皆目於罪（記）'),
    ('00_卷首', 8, '普遍都不合心意，心中都存有優劣的評判',
     '普遍都不合心意，因為群篇各都優缺點互見（俱懷優劣）', 23, '俱懷優劣主詞為群篇（記：群篇中優劣互見）'),
    ('00_卷首', 28, '第十八篇　四藥的受持與淨施',
     '第十八篇　四藥的受法與淨法', 25, '受兼手口、淨通作淨護淨（記卷下二）'),
    ('00_卷首', 54, '競相採集大會結集的大眾文句',
     '競相採集大眾部（摩訶僧祇）的文句', 26, '大眾＝大眾部、摩訶僧祇（記）'),
    ('00_卷首', 55, '以及三藏等廣為宣說',
     '以及依三藏等四大廣說來勘校', 19, '三藏等廣說＝四大廣說（記）'),
    ('00_卷首', 58, '所以文中列出四種說法，讓人勘驗得失',
     '所以本律文中列出四大廣說（四說），讓人勘驗得失', 20, '四說＝四大廣說（記：本律增四中云…有四種廣說）'),
    ('00_卷首', 59, '便一併列出正法，隨自己的意思採用',
     '便一併列出正法，任人隨意採用', 21, '隨意采用主詞為後世行事者（記科：隨人採用）'),
    ('00_卷首', 77, '其次說明諸位律師不同的執持',
     '其次說明諸位律師不同的主張', 28, '異執即是各計（記）'),
    # ---- 01a_卷上之一 ----
    ('01a_卷上之一', 16, '修持者的要旨則在於能領納戒法於心',
     '戒行則以領納戒體為其歸趣', 12, '行者＝戒行、趣＝歸趣（記：體為所歸）'),
    ('01a_卷上之一', 19, '克制心志、專一尊奉',
     '堅定心志、專一尊奉', 14, '克，猶定也（記）'),
    ('01a_卷上之一', 28, '此外還能獲得如「攝取於僧（統攝僧團）」等十種利益。',
     '此外，佛陀制戒也具足如「攝取於僧（統攝僧團）」等十種利益。', 31, '十利為制戒十利，主詞非持律人（記：又下，引制戒十利）'),
    ('01a_卷上之一', 28, '一切眾生的法身慧命由戒而得生',
     '一切眾生皆由戒法而得以存在', 32, '去增譯「法身慧命」'),
    ('01a_卷上之一', 28, '且限定要在僧團內部宣說，所以最為殊勝。',
     '且限定要在僧團內部宣說，所以最為殊勝、最為祕密。', 16, '記：故勝下合有祕字'),
]


def main():
    os.makedirs(BAK, exist_ok=True)
    chunks = sorted({e[0] for e in EDITS})
    origin = {}
    for c in chunks:
        src = os.path.join(OUT, c + '.txt')
        dst = os.path.join(BAK, c + '.txt')
        shutil.copy2(src, dst)
        origin[c] = io.open(src, encoding='utf-8', newline='').read()
        print('backup', dst, os.path.getsize(dst))

    arrs = {c: t.split('\r\n\r\n') for c, t in origin.items()}
    for c in arrs:
        while arrs[c] and arrs[c][-1].strip() == '':
            arrs[c].pop()
        assert '\r\n\r\n'.join(arrs[c]) + '\r\n\r\n' == origin[c], 'roundtrip fail %s' % c
    before = {c: list(v) for c, v in arrs.items()}

    log = []
    for c, seg, old, new, no, why in EDITS:
        idx = seg - 1
        cur = arrs[c][idx]
        n = cur.count(old)
        assert n == 1, 'seg %s#%d 條%d old 出現 %d 次: %r' % (c, seg, no, n, old[:40])
        arrs[c][idx] = cur.replace(old, new)
        log.append(dict(chunk=c, seg=seg, no=no, old=old, new=new, why=why))

    # 寫回 out（維持 \r\n\r\n 分隔、檔尾 \r\n\r\n）
    for c in chunks:
        txt = '\r\n\r\n'.join(arrs[c]) + '\r\n\r\n'
        io.open(os.path.join(OUT, c + '.txt'), 'w', encoding='utf-8', newline='').write(txt)
        print('wrote', c, 'segs', len(arrs[c]), 'bytes', len(txt.encode('utf-8')))

    # fix_re10_35.tsv
    rows = []
    for c in chunks:
        for i, (a, b) in enumerate(zip(before[c], arrs[c])):
            if a != b:
                rows.append('%s\t%s\t%d\t%s' % ('01_行事鈔', c, i + 1, b))
    io.open(os.path.join(REVIEW, 'fix_re10_35.tsv'), 'w', encoding='utf-8', newline='').write(
        '\n'.join(rows) + '\n')
    print('tsv rows', len(rows))

    json.dump(log, io.open(os.path.join(REVIEW, '_log_re10_35_apply.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
