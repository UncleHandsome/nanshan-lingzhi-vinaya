
import os, io, json, re
BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(BASE, 'TXT_分卷', '01_行事鈔')
TR = os.path.join(BASE, 'AI語譯', 'out', '01_行事鈔')
WORK = os.path.join(BASE, 'AI語譯', '_work')
keys = [k.strip() for k in io.open(os.path.join(WORK, 'fix3_keys.txt'), encoding='utf-8').read().split('\n') if k.strip()]
SYS = """你是律宗文獻的校勘者。下面給你《四分律刪繁補闕行事鈔》的原文與白話譯文，請逐段比對，找出六類問題：誤譯、漏譯、增譯、術語錯誤、分段不合、語病。
只列有問題的段落；每條給段號、原文片段、類型、問題、建議。全部無問題就回空陣列。
"""
schema = {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"seg": {"type": "STRING"}, "quote": {"type": "STRING"}, "kind": {"type": "STRING"}, "issue": {"type": "STRING"}, "fix": {"type": "STRING"}}, "required": ["seg", "quote", "kind", "issue", "fix"]}}
lines = []
for key in keys:
    src = io.open(os.path.join(SRC, key + '.txt'), encoding='utf-8').read().split('\n')[5:]
    src = '\n'.join(src).strip()
    tr = io.open(os.path.join(TR, key + '.txt'), encoding='utf-8').read()
    lines.append(json.dumps({"key": key, "request": {"contents": [{"role": "user", "parts": [{"text": SYS + "\n【原文】\n" + src + "\n\n【譯文】\n" + tr}]}], "generationConfig": {"temperature": 0.1, "maxOutputTokens": 65536, "responseMimeType": "application/json", "responseSchema": schema, "thinkingConfig": {"thinkingLevel": "high"}}}}, ensure_ascii=False))
out = os.path.join(WORK, 'batch_review4.jsonl')
io.open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('requests', len(lines))
