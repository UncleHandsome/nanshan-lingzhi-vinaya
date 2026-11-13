# -*- coding: utf-8 -*-
"""把 7K_存疑.md 拆成兩份：
  存疑_可自解.md   —— 靠原文語法、上下文、他處同詞可判
  存疑_待外部核.md —— 需查校本／大藏異文／他書互證（交給人處理）
"""
import io
import os
import re
from collections import OrderedDict

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '存疑材料', '7K_存疑.md')
OUT_MINE = os.path.join(B, '存疑材料', '存疑_可自解.md')
OUT_USER = os.path.join(B, '存疑材料', '存疑_待外部核.md')

SEG = re.compile(r'(?<![\d-])(\d{3,4}-\d{3,4})(?![\d-])')

# 需外部核：版本、校勘、訛字
USER_KW = ['疑訛', '形訛', '疑為', '疑「', '當作', '應作', '異文', '校本', '底本',
           '大正', 'CBETA', '校注', '疑脫', '疑衍', '脫文', '衍文', '疑衍',
           '疑「', '訛字', '字訛', '形近', '音誤', '音近']

# 可自解：語法、指代、兩讀
MINE_KW = ['主語', '所指', '指代', '兩讀', '二讀', '語意', '文意', '斷句',
           '兩解', '可通', '皆通', '何指', '指何', '誰']


def main():
    text = io.open(SRC, encoding='utf-8').read()
    sections = OrderedDict()
    cur = None
    for line in text.split('\n'):
        m = re.match(r'^##\s+(.+)', line)
        if m:
            cur = m.group(1).strip()
            sections.setdefault(cur, [])
            continue
        if cur is not None:
            sections[cur].append(line)

    mine, user = [], []
    for sec, lines in sections.items():
        block_mine, block_user = [], []
        cur_entry = None
        for line in lines:
            if re.match(r'^\s*(?:[-*]|\d+[.、])', line) and (SEG.search(line) or '**' in line):
                # 新條目：先結算上一條
                if cur_entry is not None:
                    (block_user if is_user(cur_entry) else block_mine).append(cur_entry)
                cur_entry = [line]
            elif cur_entry is not None:
                cur_entry.append(line)
        if cur_entry is not None:
            (block_user if is_user(cur_entry) else block_mine).append(cur_entry)
        if block_mine:
            mine.append((sec, block_mine))
        if block_user:
            user.append((sec, block_user))

    def emit(path, data, title):
        n = sum(len(b) for _, b in data)
        lines = ['# ' + title, '', '共 %d 條' % n, '']
        for sec, blocks in data:
            lines += ['## ' + sec, '']
            for b in blocks:
                lines += [x.rstrip() for x in b if x.strip()]
                lines.append('')
        io.open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        return n

    nm = emit(OUT_MINE, mine, '存疑：可自行判定')
    nu = emit(OUT_USER, user, '存疑：待外部核（需查校本／異文／他書）')
    print('可自解 %d 條 → %s' % (nm, OUT_MINE))
    print('待外部核 %d 條 → %s' % (nu, OUT_USER))


def is_user(entry_lines):
    joined = ''.join(entry_lines)
    has_user = sum(1 for k in USER_KW if k in joined)
    has_mine = sum(1 for k in MINE_KW if k in joined)
    if has_user and not has_mine:
        return True
    if has_user and has_mine:
        return has_user > has_mine
    return False


if __name__ == '__main__':
    main()