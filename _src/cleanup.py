# -*- coding: utf-8 -*-
"""清理專案資料夾：刪除暫存、舊版、重複與可重建的中間檔"""
import os, shutil, glob, io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
log = []
freed = 0


def size_of(p):
    if os.path.isfile(p):
        return os.path.getsize(p)
    t = 0
    for r, d, fs in os.walk(p):
        for f in fs:
            try:
                t += os.path.getsize(os.path.join(r, f))
            except OSError:
                pass
    return t


def rm(p):
    global freed
    if not os.path.exists(p):
        return
    s = size_of(p)
    if os.path.isdir(p):
        shutil.rmtree(p, ignore_errors=True)
    else:
        os.remove(p)
    freed += s
    log.append('%-60s %6.1f MB' % (os.path.relpath(p, B), s / 1048576))


# 1. 根目錄暫存
for p in glob.glob(os.path.join(B, '_tmp*')):
    rm(p)

# 2. 舊版 PDF
rm(os.path.join(B, '白話', '_舊版'))

# 3. 白話根目錄的重複 PDF（對照本已有）
target = os.path.join(B, '白話', '對照本')
for p in glob.glob(os.path.join(B, '白話', '*.pdf')):
    if os.path.exists(os.path.join(target, os.path.basename(p))):
        rm(p)

# 4. 舊備份
rm(os.path.join(B, 'AI語譯', '_bak_20261105_2030'))

# 5. _work 內可重建的批次與大型 jsonl
W = os.path.join(B, 'AI語譯', '_work')
for d in ['align_ai', 'align_ai2', 'align_fix', 'align_fix2', 'align_ys',
          'new2_sec', 'new2_ai', 'new3_sec', 'new3_ai', 'new4_sec', 'new4_ai',
          'new5_sec', 'misstr', 'miss2', 'miss3', 'miss4', 'punc_ys', 'retr']:
    rm(os.path.join(W, d))
for p in glob.glob(os.path.join(W, '*.jsonl')):
    if os.path.getsize(p) > 1024 * 1024:
        rm(p)

# 6. _build（腳本在 _src，此處只是暫存與舊 XML）
rm(os.path.join(B, '_build'))

# 7. 材料資料夾裡的大型原始 md（new*.txt 已保留）
for d in ['合編材料', '業疏材料']:
    for p in glob.glob(os.path.join(B, d, '*.md')):
        rm(p)

io.open(os.path.join(B, '清理紀錄.txt'), 'w', encoding='utf-8').write(
    '清理時間：2026-11-06\n清理項目（可重建或已淘汰）：\n' + '\n'.join(log) +
    '\n\n合計釋放：%.1f MB\n' % (freed / 1048576))
print('釋放 %.1f MB' % (freed / 1048576))
print('\n'.join(log[-12:]))
