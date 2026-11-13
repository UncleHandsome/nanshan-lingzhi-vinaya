# -*- coding: utf-8 -*-
"""1822：11d#14-17 想/疑句式与术语统一（段内定点替换）。"""
import io, json, sys
sys.path.insert(0, '.')
import _z6_lib as L

CH = '11d_中四上'
PARAS = [14, 15, 16, 17]
REPL = [
    (u'約定對象四句', u'就人（對象）分別四句'),
    (u'約定事法五句', u'就法（媒嫁之事）分別五句'),
    (u'三十迴僧物戒四句', u'第三十、迴僧物戒四句'),
    (u'四歎身戒五句', u'第四、歎身（索供）戒五句'),
    (u'五媒嫁戒二重', u'第五、媒嫁戒二重'),
    (u'六作無主房戒四重', u'第六、無主房戒四重'),
    (u'所處難處五句', u'處所有難五句'),
    (u'所處妨礙處五句', u'處所有妨五句'),
    (u'不是麁語懷疑不是麁語', u'境非麁語，疑是否為非麁語'),
    (u'不是麁語作麁語想', u'境非麁語，作麁語想'),
    (u'非人女作人女想', u'非人女，作人女想'),
    (u'人女作人女想', u'（對象）人女，作人女想'),
    (u'人女懷疑是人女', u'人女，疑（是否為人女）'),
    (u'非人女懷疑是非人女', u'非人女，疑（是否為非人女）'),
    (u'人女作非人女想', u'人女，作非人女想'),
    (u'是媒嫁懷疑是媒嫁', u'是媒嫁，疑是否為媒嫁'),
    (u'是媒嫁作不是媒嫁想', u'是媒嫁，作非媒嫁想'),
    (u'不是媒嫁作媒嫁想', u'境非媒嫁，作媒嫁想'),
    (u'不是媒嫁懷疑不是媒嫁', u'境非媒嫁，疑是否為非媒嫁'),
    (u'是媒嫁作媒嫁想', u'是媒嫁，作媒嫁想'),
    (u'未得處分作未處分想', u'未經僧處分，作未經處分想'),
    (u'未得處分懷疑是未處分', u'未經僧處分，疑是否未經處分'),
    (u'未得處分作已處分想', u'未經僧處分，作已處分想'),
    (u'已得處分作未處分想', u'已經僧處分，作未經處分想'),
    (u'已得處分懷疑是已處分', u'已經僧處分，疑是否已經處分'),
    (u'有災難處作有難處想', u'處所有難（傷生之虞），作有難想'),
    (u'有災難處懷疑是有難處', u'處所有難，疑是否有難'),
    (u'有災難處作無難處想', u'處所有難，作無難想'),
    (u'無災難處作有難處想', u'處所無難，作有難想'),
    (u'無災難處懷疑是無難處', u'處所無難，疑是否無難'),
    (u'有妨害處作有妨處想', u'處所有妨（無空地迴轉），作有妨想'),
    (u'有妨害處懷疑是有妨處', u'處所有妨，疑是否有妨'),
    (u'有妨害處作無妨處想', u'處所有妨，作無妨想'),
    (u'無妨害處作有妨處想', u'處所無妨，作有妨想'),
    (u'無妨害處懷疑是無妨處', u'處所無妨，疑是否無妨'),
    (u'施主已應許作已許想〔犯波逸提〕', u'（施主）已許與僧之物，作已許想〔犯波逸提（捨墮）〕'),
    (u'施主已應許懷疑是已許', u'（施主）已許與僧之物，疑是否已許'),
    (u'施主未應許作已許想', u'（施主）未許與僧，作已許想'),
    (u'施主未應許懷疑是未許', u'（施主）未許與僧，疑是否未許'),
]

t, s = L.paras(CH)
ps = t.split(s)
before_lines = t.count('\n')
report = []
total = 0
for i in PARAS:
    p = ps[i - 1]
    for old, new in REPL:
        c = p.count(old)
        if c:
            p = p.replace(old, new)
            total += c
            report.append((i, old, c))
    ps[i - 1] = p
missing = []
for old, new in REPL:
    if not any(r[1] == old for r in report):
        missing.append(old)

new_t = s.join(ps)
assert len(ps) == len(t.split(s)), 'para count changed'
assert new_t.count('\n') == before_lines, 'line count changed'
L.backup(CH)
L.wr(L.os.path.join(L.OUTDIR, CH + '.txt'), new_t)
for r in report:
    print(r[0], r[2], r[1])
print('MISSING', len(missing))
for m in missing:
    print('  miss:', m)
print('TOTAL', total)
stats = {"n": 1822, "edits": total, "segs": 4, "yi": total, "run": 0,
         "veto": 1, "doubt": 0,
         "note": u"約=就非約定；想/疑分境與心；難處=傷生之虞；妨處=無空地迴轉；處分=僧指授；已許=施主許僧"}
with io.open('_z7_log.jsonl', 'a', encoding='utf-8') as f:
    f.write(json.dumps(stats, ensure_ascii=False) + '\n')
