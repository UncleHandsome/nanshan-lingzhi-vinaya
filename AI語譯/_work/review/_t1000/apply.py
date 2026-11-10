# -*- coding: utf-8 -*-
"""套用 1000 檔校閱修訂：逐段字串替換，先驗證片段唯一，再輸出 TSV 與（可選）寫回。"""
import io, os, sys, json, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
REV = os.path.join(B, 'AI語譯', '_work', 'review')
BAK = os.path.join(B, '歸檔', '1000檔修正前')

# (gid, book, chunk, seg, [(old, new), ...], note)
EDITS = [
    ('01_行事鈔/00_卷首#6', '01_行事鈔', '00_卷首', 6,
     [('僧團的綱維要維持，同異之間必須加以區別。',
       '僧團綱紀的維持，各生異見；同異之間，互相強分。')], '眾網維持、同異區別為致令之結果'),
    ('01_行事鈔/00_卷首#8', '01_行事鈔', '00_卷首', 8,
     [('有長遠見解的一定記錄下來', '凡有所長的見解必定記錄下來')], '長見＝有所長之見'),
    ('01_行事鈔/01b_卷上之一#39', '01_行事鈔', '01b_卷上之一', 39,
     [('如果在屋舍內，隨其走出幾次；', '如果在屋舍內，只要一跨出門戶即失欲；')], '隨幾過出＝一過出即失'),
    ('01_行事鈔/07b_卷中之三#30', '01_行事鈔', '07b_卷中之三', 30,
     [('若是受持不作餘食法之行者，可不起立迎敬，只需告知說：『我受持了不作餘食法』，便可坐著繼續進食。',
       '若是受食後未作餘食法的人，可不起立迎敬，只需告知說：『我已受食，未作餘食法』，便可坐著繼續進食。')],
     '受＝受食，非受持'),
    ('01_行事鈔/07b_卷中之三#32', '01_行事鈔', '07b_卷中之三', 32,
     [('律不犯者：', '《四分律》中不結罪（不犯）的情況如下：'),
      ('受持不作餘食法之頭陀行者（上行不犯）；', '未經受取即先為之作餘食法；')],
     '段首半譯＋不受作餘食法'),
    ('01_行事鈔/07b_卷中之三#35', '01_行事鈔', '07b_卷中之三', 35,
     [('皆是以山林中坐禪比丘貪圖打坐不出行乞食而儲存食物為緣起；', '皆是以山林中坐禪比丘為緣起；')],
     '刪除增譯動機'),
    ('01_行事鈔/07d_卷中之三#4', '01_行事鈔', '07d_卷中之三', 4,
     [('則不算犯戒，並開許免除親教師（和尚）的墮罪（波逸提），以及其餘參與者的突吉羅罪。',
       '則不算犯戒；律制開緣減罪：親教師（和尚）仍結墮罪（波逸提），其餘參與的僧人則減為突吉羅罪。')],
     '開和尚墮、餘人吉羅'),
    ('01_行事鈔/01a_卷上之一#28', '01_行事鈔', '01a_卷上之一', 28,
     [('三是若有疑悔時不需向他人請問；', '三是使自己不致心生疑悔而需向他人請問；'),
      ('這就像濾水免殺水中蟲的譬喻一樣。', '這就像寧可渴死也不飲有蟲之水的譬喻一樣。')],
     '不欲有疑悔請問他人／飲水殺蟲之喻'),
]


def load(path):
    raw = io.open(path, 'rb').read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    text = raw.decode('utf-8-sig')
    sep = '\r\n\r\n' if '\r\n\r\n' in text else '\n\n'
    return text, sep, bom


def save(path, text, bom):
    data = text.encode('utf-8')
    if bom:
        data = b'\xef\xbb\xbf' + data
    io.open(path, 'wb').write(data)


def main():
    apply = '--apply' in sys.argv
    rows = []
    report = []
    for gid, book, chunk, seg, pairs, note in EDITS:
        p = os.path.join(OUT, book, chunk + '.txt')
        text, sep, bom = load(p)
        paras = text.split(sep)
        # 只取非空段落定位（段號以非空段落計）
        idxs = [i for i, x in enumerate(paras) if x.strip()]
        para = paras[idxs[seg-1]]
        newpara = para
        for old, new in pairs:
            n = newpara.count(old)
            assert n == 1, '片段出現 %d 次: %s | %s' % (n, gid, old)
            newpara = newpara.replace(old, new, 1)
        assert newpara != para
        assert '\n' not in newpara and '\t' not in newpara
        rows.append((book, chunk, str(seg), newpara))
        report.append(dict(gid=gid, book=book, chunk=chunk, seg=seg, note=note,
                           old=para, new=newpara))
        if apply:
            os.makedirs(os.path.join(BAK, book), exist_ok=True)
            bp = os.path.join(BAK, book, chunk + '.txt')
            if not os.path.exists(bp):
                shutil.copy2(p, bp)
            paras[idxs[seg-1]] = newpara
            save(p, sep.join(paras), bom)
            # 驗證段數不變
            t2, sep2, _ = load(p)
            n1 = len([x for x in text.split(sep) if x.strip()])
            n2 = len([x for x in t2.split(sep2) if x.strip()])
            assert n1 == n2, 'paracount changed %s %s -> %s' % (p, n1, n2)

    # TSV
    tsv = '\n'.join('\t'.join(r) for r in rows) + '\n'
    io.open(os.path.join(REV, 'fix_1000.tsv'), 'w', encoding='utf-8', newline='\n').write(tsv)
    # 錯位（無）
    io.open(os.path.join(REV, '錯位_1000.tsv'), 'w', encoding='utf-8', newline='\n').write('')
    json.dump(report, io.open(os.path.join(REV, '_t1000', 'fixreport.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('rows', len(rows), 'apply', apply)
    for r in report:
        print('---', r['gid'])
        print('OLD:', r['old'][:120])
        print('NEW:', r['new'][:120])


if __name__ == '__main__':
    main()
