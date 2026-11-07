# -*- coding: utf-8 -*-
"""產出可直接貼給 AI 的行事鈔未譯段落翻譯提示詞"""
import glob, os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

items = []
for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', '01_行事鈔', '*.txt'))):
    k = os.path.basename(f)[:-4]
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    for i in range(min(len(sp), len(tt))):
        a, b = han(sp[i]), han(tt[i])
        if len(a) < 15:
            continue
        same = a[:20] == b[:20]
        plain = (a.count('，') + a.count('。')) > 3 and ('的' not in b and '是' not in b and '這' not in b and '了' not in b)
        if same or plain:
            items.append((k, i + 1, sp[i], sp[i - 1] if i else ''))

head = '''你是律學古籍翻譯專家，專精唐代道宣律師《四分律刪繁補闕行事鈔》與宋代元照律師《資持記》。

## 任務
下面每一段都是《行事鈔》原文，目前還沒有白話翻譯（或誤把原文當譯文）。請逐段翻成現代白話。

## 規則
1. 一段對一段，編號不可改變、不可合併、不可省略。
2. 只回 JSON，格式如下：
   ```json
   {"05a": {"14": "白話…", "15": "白話…"}}
   ```
3. 白話要通順可讀，但義理不可增減。
4. 律學術語（波羅夷、僧伽婆尸沙、偷蘭遮、波逸提、突吉羅、羯磨、說恣等）保留原詞，可在白話中自然帶出。
5. 原文有明顯錯字或闕字，照文義順譯，不自行考證。
6. 若某段是簡短的科判或戒條標題，白話也可以簡短。

## 待譯段落
'''

body = []
for k, idx, txt, prev in items:
    body.append('### %s 第 %d 段' % (k, idx))
    if prev:
        body.append('- 前一段（僅供理解，不必翻）：%s' % prev[:60])
    body.append('- 原文：%s' % txt)
    body.append('')

tail = '''## 回傳格式（複製這段填空即可）

```json
{"05a": {"14": "", "15": "", "16": "", "17": ""},
 "05b": {"16": ""},
 "06b": {"27": "", "35": ""},
 "08c": {"38": ""}}
```
'''
io.open(os.path.join(B, '提示詞_行事鈔未譯8段.md'), 'w', encoding='utf-8').write(head + '\n'.join(body) + tail)
print('產出', len(items), '段 → 提示詞_行事鈔未譯8段.md')
