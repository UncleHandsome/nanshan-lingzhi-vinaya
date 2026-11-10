# -*- coding: utf-8 -*-
"""Parse 校閱_單段_前1000個校閱結果.md into structured entries."""
import io, os, re, json, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '校閱_單段_前1000個校閱結果.md')
OUT = os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'entries.json')

lines = io.open(SRC, encoding='utf-8').read().split('\n')

re_head = re.compile(r'^(?:###\s*)?(.+?/[\w\u4e00-\u9fff]+#\d+)\s*(?:｜\s*(P\d)\s*｜\s*(.*))?$')
re_doubt = re.compile(r'^(?:###\s*)?存疑\s*｜\s*(.+?/[\w\u4e00-\u9fff]+#\d+)\s*$')
re_chunk = re.compile(r'^##\s+(\d{5})_(.+)$')
re_kv = re.compile(r'^-?\s*(原文起首|問題|依據|建議|信心|存疑|疑點|說明|補充)\s*：\s*(.*)$')

cur_chunk = ''
entries = []
cur = None

def flush():
    global cur
    if cur is not None:
        entries.append(cur)
    cur = None

i = 0
while i < len(lines):
    ln = lines[i].rstrip('\n')
    m = re_chunk.match(ln)
    if m:
        flush()
        cur_chunk = m.group(1) + '_' + m.group(2)
        i += 1
        continue
    if ln.startswith('=== 本檔結束 ==='):
        flush()
        i += 1
        continue
    m = re_doubt.match(ln)
    if m:
        flush()
        gid = m.group(1)
        book, rest = gid.split('/', 1)
        chunk, seg = rest.rsplit('#', 1)
        cur = dict(section=cur_chunk, gid=gid, book=book, chunk=chunk, seg=int(seg),
                   level='存疑', cat='存疑', orig='', problem='', basis='', suggestion='',
                   doubt='', conf='', raw=[ln])
        i += 1
        continue
    m = re_head.match(ln)
    if m and not ln.startswith('檔案編號') and not ln.startswith('已檢查'):
        flush()
        gid = m.group(1)
        book, rest = gid.split('/', 1)
        chunk, seg = rest.rsplit('#', 1)
        cur = dict(section=cur_chunk, gid=gid, book=book, chunk=chunk, seg=int(seg),
                   level=m.group(2) or '', cat=(m.group(3) or '').strip(),
                   orig='', problem='', basis='', suggestion='', doubt='', conf='', raw=[ln])
        i += 1
        continue
    m = re_kv.match(ln)
    if m and cur is not None:
        k, v = m.group(1), m.group(2).strip()
        cur['raw'].append(ln)
        if k == '原文起首':
            cur['orig'] = v
        elif k == '問題':
            cur['problem'] = v
        elif k == '依據':
            cur['basis'] = v
        elif k == '建議':
            cur['suggestion'] = v
        elif k == '信心':
            cur['conf'] = v
        elif k in ('存疑', '疑點'):
            cur['doubt'] = v
        i += 1
        continue
    if ln.strip() and cur is not None and not ln.startswith('##'):
        cur['raw'].append(ln)
    i += 1
flush()

# dedupe identical (gid, level, cat, problem)
seen = {}
uniq = []
for e in entries:
    key = (e['gid'], e['level'], e['cat'], e['problem'][:60])
    if key in seen:
        seen[key]['dup'] = seen[key].get('dup', 0) + 1
        continue
    seen[key] = e
    uniq.append(e)

json.dump(dict(all=entries, uniq=uniq), io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('total entries', len(entries), 'uniq', len(uniq))
for e in uniq:
    print('%s | %s | %s | %s' % (e['gid'], e['level'], e['cat'], (e['problem'] or e['doubt'])[:40]))
