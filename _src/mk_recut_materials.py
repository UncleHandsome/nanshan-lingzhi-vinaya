# -*- coding: utf-8 -*-
"""產「重切材料」：把 GAP／硬切合併群組切成 ~20K bytes 一檔，附提示詞。

來源：重作材料_長段/GAP合併預覽_20261124.json（groups）
輸出：重作材料_長段/重切材料_20K_20261124/0001.md …

原文取法與網站一致：display_source 有標點就用 display，否則用 source。
"""
import io
import json
import os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '重作材料_長段', 'GAP合併預覽_20261124.json')
OUT = os.path.join(B, '重作材料_長段', '重切材料_20K_20261124')
LIMIT = 20000
BOOKS = ['xingshichao', 'jieshu', 'yeshu', 'nicao', 'yichao', 'zhichi']

PROMPT = '''請把下面每一組「合併原文＋合併白話」重新切成以句讀為界的段落。

【切分規則】
1. 依原文的 。！？；： 與文義切分；每段 1–3 句，不得跨句腰斬，也不得切斷詞語（例如「木叉」不可拆成「木」「叉」）。
2. 白話依同一落點切分，與原文各段一一對應；順序、字句不可改動，不可增刪、不可改寫。
3. 若白話與原文段落無法精確一一對應，保持原順序、依白話句讀就近對齊，並在 note 說明。
4. 原文、白話都必須完整保留；切完後逐字接回應與原輸入相同（標點可依段界補足句末標點）。

【輸出】
只輸出 JSONL，每行一段（不要 code fence、前言、解釋）：
{"book_id":"書代號","key":"第一列代號","part":1,"source":"該段原文","translation":"該段白話","note":"可留空"}

book_id 用：xingshichao／jieshu／yeshu／nicao／yichao／zhichi。
key 填該組「##」列第一列的代號。part 由 1 起遞增。

'''


def block(g):
    return '\n'.join(['## %s／%s' % (g['book'], '＋'.join(g['keys'])),
                      '', '### 原文', '', g['source'],
                      '', '### 白話', '', g['translation'], ''])


def main():
    groups = [g for g in json.load(io.open(SRC, encoding='utf-8'))['groups'] if g.get('need_cut', True)]
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    idx = 0
    buf = []
    size = 0

    def flush():
        nonlocal idx, buf, size
        if not buf:
            return
        idx += 1
        io.open(os.path.join(OUT, '%04d.md' % idx), 'w',
                encoding='utf-8', newline='\n').write(PROMPT + '\n' + '\n'.join(buf))
        buf = []
        size = 0

    for g in groups:
        b = block(g)
        n = len(b.encode('utf-8')) + 1
        if buf and size + n > LIMIT:
            flush()
        buf.append(b)
        size += n
    flush()
    print('groups', len(groups), 'files', idx, OUT)


if __name__ == '__main__':
    main()
