# -*- coding: utf-8 -*-
"""掃描 30 篇：未譯（譯文≈原文）與空譯（極短），產出待處理清單與提示詞"""
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
        if len(a) < 12:
            continue
        same = a[:20] == b[:20]
        empty = len(b) < 4
        plain = (a.count('，') + a.count('。')) > 3 and not any(c in b for c in '的是這了也就')
        if same or empty or plain:
            items.append((k, i + 1, sp[i], tt[i], sp[i - 1] if i else ''))

lines = ['# 會本剩餘未譯段落（自動掃描）', '', '共 %d 段' % len(items), '']
for k, idx, src, tr, prev in items:
    lines.append('## %s 第 %d 段' % (k, idx))
    lines.append('- 原文：%s' % src)
    lines.append('- 現譯文（有問題）：%s' % (tr[:40] if tr else '（空）'))
    lines.append('')
io.open(os.path.join(B, '待處理_會本剩餘未譯.md'), 'w', encoding='utf-8').write('\n'.join(lines))

prompt = ['你是律學古籍翻譯專家，專精道宣律師《四分律行事鈔》與元照律師《資持記》。', '',
          '## 任務', '下列《行事鈔》原文目前未譯或譯文有誤，請逐段翻成現代白話。', '',
          '## 規則', '1. 一段對一段，編號不可改。', '2. 只回 JSON：{"chunk": {"段號": "白話…"}}',
          '3. 術語保留（波羅夷、僧殘、偷蘭遮、波逸提、突吉羅、羯磨等）。', '4. 義理不可增減，不必考證。', '',
          '## 待譯段落', '']
for k, idx, src, tr, prev in items:
    prompt.append('### %s 第 %d 段' % (k, idx))
    prompt.append('- 原文：%s' % src)
    prompt.append('')
prompt.append('## 回傳格式')
prompt.append('```json')
prompt.append('{')
for k in sorted({x[0] for x in items}):
    segs = [x[1] for x in items if x[0] == k]
    prompt.append('  "%s": {%s}' % (k, ', '.join('"%d": ""' % s for s in segs)))
prompt.append('}')
prompt.append('```')
io.open(os.path.join(B, '提示詞_會本剩餘未譯.md'), 'w', encoding='utf-8').write('\n'.join(prompt))
print('flagged', len(items))
for k, idx, src, tr, prev in items:
    print(k, idx, src[:30])
