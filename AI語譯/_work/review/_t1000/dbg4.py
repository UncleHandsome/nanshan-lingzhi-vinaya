# -*- coding: utf-8 -*-
import io, re, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
lines = io.open(os.path.join(B, '校閱_單段_前1000個校閱結果.md'), encoding='utf-8').read().split('\n')
re_head = re.compile(r'^(?:###\s*)?(.+?/[\w\u4e00-\u9fff]+#\d+)\s*(?:｜\s*(P\d)\s*｜\s*(.*))?$')
re_doubt = re.compile(r'^(?:###\s*)?存疑\s*｜\s*(.+?/[\w\u4e00-\u9fff]+#\d+)\s*$')
re_chunk = re.compile(r'^##\s+(\d{5})_(.+)$')
re_kv = re.compile(r'^-?\s*(原文起首|問題|依據|建議|信心|存疑|疑點|說明|補充)\s*：\s*(.*)$')
nh = nd = nk = 0
for i, ln in enumerate(lines, 1):
    ln = ln.rstrip('\n')
    if re_chunk.match(ln):
        continue
    if ln.startswith('=== 本檔結束 ==='):
        continue
    if re_doubt.match(ln):
        nd += 1
        print('DOUBT', i, ln[:50])
        continue
    if re_head.match(ln) and not ln.startswith('檔案編號') and not ln.startswith('已檢查'):
        nh += 1
        continue
    if re_kv.match(ln):
        nk += 1
print('heads', nh, 'doubts', nd, 'kv', nk)
