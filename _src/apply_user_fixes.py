# -*- coding: utf-8 -*-
"""依使用者回覆修正 篇11/18/19/21/23 的殘留問題"""
import io, os, re, json
from docx import Document
from docx.shared import Pt

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WH = os.path.join(B, '白話')

# ---------- 篇11：記78 前半（夾註）歸鈔19，鈔20 插在中間 ----------
fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇11.json')
m = {'splits': []}
if os.path.exists(fp):
    m = json.load(io.open(fp, encoding='utf-8-sig'))
m['splits'] = [e for e in m.get('splits', []) if int(e['n']) != 78]
m['splits'].append({'n': 78, 'base': 19, 'markers': ['初門，通明中'], 'targets': [19, 21], 'flex': True})
json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇11 記78 flex 已寫入')

def paras(doc):
    return [p for p in doc.paragraphs]

def set_text(p, text):
    for r in p.runs:
        r.text = ''
    if p.runs:
        p.runs[0].text = text
    else:
        p.add_run(text)

# ---------- 篇21：記16、記42 譯文 ----------
f21 = os.path.join(WH, '會本_篇21_頭陀行儀.docx')
d = Document(f21)
ps = d.paragraphs
for i, p in enumerate(ps):
    t = p.text.strip()
    if t.startswith('【記016】（前半）'):
        body = ps[i + 1]
        if '出要' not in body.text:
            set_text(body, body.text.rstrip('。') + '。「出要」，就是證悟真理。')
    if t.startswith('【記016】（中）') or t.startswith('【記016】（後）'):
        body = ps[i + 1]
        body_text = body.text
        body_text = body_text.replace('「出要」，就是證悟真理。', '', 1)
        set_text(body, body_text.lstrip())
    if t.startswith('【記042】（前半）'):
        body = ps[i + 1]
        if '崇' not in body.text:
            set_text(body, body.text.rstrip('。') + '。「崇」就是尊重的意思，是指上等行持中尤其看重阿蘭若（十種利益如前文所述）。')
    if t.startswith('【記042】（後半）'):
        body = ps[i + 1]
        body_text = body.text.replace('「崇」就是尊重的意思，是指上等行持中尤其看重阿蘭若（十種利益如前文所述）。', '', 1)
        set_text(body, body_text.lstrip())
d.save(f21)
print('篇21 譯文已修')

# ---------- 篇19：記23 重複句（中片尾與後片頭）----------
f19 = os.path.join(WH, '會本_篇19_鉢器制聽.docx')
d = Document(f19)
ps = d.paragraphs
for i, p in enumerate(ps):
    if p.text.strip().startswith('【記023】（中）'):
        body = ps[i + 1]
        bt = body.text
        k = bt.rfind('初文《四分》七段')
        if k > 0:
            set_text(body, bt[:k].rstrip())
            print('篇19 記23 中片尾重複句已刪')
d.save(f19)

# ---------- 篇23：記058 補兩句譯文 ----------
f23 = os.path.join(WH, '會本_篇23_訃請設則.docx')
d = Document(f23)
ps = d.paragraphs
for i, p in enumerate(ps):
    if p.text.strip().startswith('【記058】'):
        body = ps[i + 1]
        if '申時' not in body.text:
            set_text(body, body.text.rstrip() + '下一科引用經典說明佛陀在世時的說法儀軌，令後世弟子依循仿效。「晡」就是申時（下午三點至五點）。')
            print('篇23 記58 譯文已補')
d.save(f23)
print('done')
