# -*- coding: utf-8 -*-
"""挑選問題段落，產生 Gemini batch 請求檔。"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
BAKDIR = os.path.join(B, 'AI語譯', '回譯測試')
os.makedirs(BAKDIR, exist_ok=True)

SRC_MAP = {
    '01_行事鈔': 'TXT_分卷/01_行事鈔',
    '02_戒疏': 'TXT_分卷/02_戒疏',
    '03_業疏': 'TXT_分卷_標點/03_業疏',
}

# (書, chunk, 段序, 段號, 問題簡述)
PICKS = [
    ('02_戒疏', '02a_卷一上之二', 86, '503-0001', '引號內塞補語、牒字被改'),
    ('02_戒疏', '02b_卷一上之二', 113, '518-0010', '整句重出未刪'),
    ('02_戒疏', '04c_卷一下之二', 91, '626-0010', '「單意」定義讀反'),
    ('02_戒疏', '04c_卷一下之二', 102, '627-0006', '「位列」誤作階位'),
    ('02_戒疏', '04c_卷一下之二', 144, '630-0010', '「律判不定」軸線偏移'),
    ('02_戒疏', '05d_卷二上之一', 81, '681-0013', '「制」與「塵」兩處術語讀反'),
    ('02_戒疏', '07b_卷二上之三', 2, '733-0001', '「一切共」誤作「平分」'),
    ('02_戒疏', '11b_卷三上之二', 63, '912-0001', '「通塞」術語讀反'),
    ('02_戒疏', '15a_卷三下之三', 21, '1016-0011', '牒字「此初」誤作判斷句'),
    ('02_戒疏', '16b_卷四上之一', 38, '1080-0011', '「行罵戒二」戒次誤讀'),
    ('02_戒疏', '16c_卷四上之一', 109, '1100-0006', '「使人無犯」主客倒置'),
    ('03_業疏', '01b_卷一之一', 19, '2299', '「作與無作」加「戒」窄化'),
    ('01_行事鈔', '10b_卷下之二', 1, '339-0001', '「淨／不淨」誤作「乾淨」'),
    ('01_行事鈔', '12a_卷下之四', 44, '407-0004', '「熱癊」生僻字未註'),
]

PROMPT = """你是南山律典的資深譯者，專精《四分律》與道宣律師的著作。

下面是原典的一段原文，以及目前的白話譯文。目前的譯文可能有錯——已知它在某些地方術語讀錯、主客倒置、或加了原文沒有的意思。

請你**重新翻譯**這一段，要求：

1. 術語必須依律學定義，不可望文生義。例如「制」是制戒不是制伏；「通塞」是通（普遍）與塞（局限）不是通達與閉塞；「塵」在此類語境多指煩惱塵垢；「淨」指如法淨施不是乾淨。
2. 引號「」內的文字必須是原文用字，不可改寫、不可塞入補語。
3. 科判引字（如「初」「所」「又」「如」）是定位字，應保留原字並作「『初』字以下」這類表述。
4. 不加原文沒有的意思，也不漏掉原文的意思。
5. 譯文要通順的現代白話，但不要口語化到失去莊重。
6. 括號夾註只用在「術語還原」（把誤譯的名相改回正名），不要自創定義。

直接輸出譯文，不要解釋你的判斷。

【原文】
{src}

【目前譯文（可能有誤）】
{cur}
"""

rows = []
for book, chunk, idx, segid, note in PICKS:
    sd = os.path.join(B, SRC_MAP[book].replace('/', os.sep))
    sp = os.path.join(sd, chunk + '.txt')
    tp = os.path.join(OUT, book, chunk + '.txt')
    if not (os.path.exists(sp) and os.path.exists(tp)):
        print('缺檔', book, chunk)
        continue
    raw = io.open(sp, encoding='utf-8', errors='ignore').read().split('\n')
    src = [x.strip() for x in (raw[5:] if book != '03_業疏' else raw) if x.strip()]
    tr = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8', errors='ignore').read()) if x.strip()]
    if idx > len(src) or idx > len(tr):
        print('段序超界', chunk, idx, len(src), len(tr))
        continue
    rows.append({
        'segid': segid,
        'book': book,
        'chunk': chunk,
        'idx': idx,
        'note': note,
        'src': src[idx - 1],
        'cur': tr[idx - 1],
    })

# 寫對照表
with io.open(os.path.join(BAKDIR, '原譯對照.tsv'), 'w', encoding='utf-8') as f:
    f.write('段號\t書\tchunk\t段序\t問題\t原文\t現譯\n')
    for r in rows:
        f.write('\t'.join([r['segid'], r['book'], r['chunk'], str(r['idx']), r['note'],
                           r['src'].replace('\t', ' '), r['cur'].replace('\t', ' ')]) + '\n')

# 寫 batch JSONL
jl = os.path.join(BAKDIR, 'batch_input.jsonl')
with io.open(jl, 'w', encoding='utf-8', newline='\n') as f:
    for i, r in enumerate(rows, 1):
        req = {
            'key': 'req-%02d' % i,
            'request': {
                'contents': [{'role': 'user', 'parts': [{'text': PROMPT.format(src=r['src'], cur=r['cur'])}]}],
                'generationConfig': {
                    'thinkingConfig': {'thinkingLevel': 'max', 'includeThoughts': False},
                    'maxOutputTokens': 32768,
                    'temperature': 0.2,
                },
            },
        }
        f.write(json.dumps(req, ensure_ascii=False) + '\n')

print('產生 %d 段' % len(rows))
print('JSONL：', jl, os.path.getsize(jl), 'bytes')
for r in rows:
    print('  %-10s %-20s #%-3d %s' % (r['segid'], r['chunk'][:18], r['idx'], r['note']))