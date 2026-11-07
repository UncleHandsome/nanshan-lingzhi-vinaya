# -*- coding: utf-8 -*-
"""Optional: fixes for rows whose review target was mislocated (correct seg recorded)."""
import io, os, re, sys

REV = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.abspath(os.path.join(REV, '..', '..')), 'out', '02_戒疏')

JOBS = [
 ('07a_卷二上之三', 35, [("「行醫師」，依照論典", "「胸行師」，依照論典")]),
 ('09a_卷二下之二', 62, [("或許是因為爭食奪命或暴食傷身",
                           "是因為吃大摶飯可能導致他人分不到飲食而受飢害的緣故")]),
 ('09a_卷二下之二', 82, [("「度量」，就是佛制長十二肘、廣七肘的具體規制",
                           "「度量」，就是指佛制長度與寬度的法則規制")]),
 ('11c_卷三上之二', 23, [("不疊敷具戒", "不揲坐具戒")]),
 ('16b_卷四上之一', 146, [("與未受具足戒人同宿超過限期戒分為五個部分。",
                            "與未受具足戒人同宿超過限期戒第五。")]),
 ('19d_卷四下之一', 84, [("理應允許他重新再聽一次即可",
                           "理應像對耳聾聽不清的人一樣給予開許")]),
 ('21c_卷四下之三', 28, [("輕忽過惡而積極修善", "息除過患而積極修善")]),
 ('21c_卷四下之三', 101, [("你是從那位龍公的分會編纂道場來的嗎？",
                            "你曾參與那位龍公分會編纂的法席嗎？")]),
]

pc = {}
def paras(chunk):
    if chunk not in pc:
        txt = io.open(os.path.join(OUT, chunk + '.txt'), encoding='utf-8').read()
        pc[chunk] = [x.strip() for x in re.split(r'\r?\n\s*\r?\n', txt) if x.strip()]
    return pc[chunk]

errs = []
outrows = []
for chunk, seg, edits in JOBS:
    cur = paras(chunk)[seg - 1]
    new = cur
    for old, rep in edits:
        c = new.count(old)
        if c != 1:
            errs.append('%s#%d count=%d %s' % (chunk, seg, c, old[:30]))
            continue
        new = new.replace(old, rep)
    if new == cur:
        errs.append('%s#%d unchanged' % (chunk, seg))
    outrows.append((chunk, seg, new))

if errs:
    print('ERRORS', errs)
    sys.exit(1)
p = os.path.join(REV, 'fix_loc_g1_reloc.tsv')
with io.open(p, 'w', encoding='utf-8', newline='\n') as w:
    for chunk, seg, new in outrows:
        w.write('02_戒疏\t%s\t%d\t%s\n' % (chunk, seg, new))
print('wrote', len(outrows))
with io.open(os.path.join(REV, '_g1b_reloc_out.txt'), 'w', encoding='utf-8') as w:
    for chunk, seg, new in outrows:
        w.write('## %s #%d\n%s\n\n' % (chunk, seg, new))
