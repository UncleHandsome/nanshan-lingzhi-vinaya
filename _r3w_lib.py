import re, os, sys, json, shutil

BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

def path_of(book, chunk):
    return os.path.join(BASE, 'AI語譯', 'out', book, chunk + '.txt')

def read_text(book, chunk):
    with open(path_of(book, chunk), 'rb') as f:
        return f.read().decode('utf-8')

def split_parts(text):
    # even index = paragraph content, odd = separator
    return re.split(r'((?:\r?\n){2,})', text)

def para_of(text, idx1):
    parts = split_parts(text)
    blocks = parts[0::2]
    if idx1 < 1 or idx1 > len(blocks):
        raise IndexError(f'para {idx1} out of range {len(blocks)}')
    return blocks[idx1-1]

def replace_para(text, idx1, new):
    parts = split_parts(text)
    blocks = parts[0::2]
    if idx1 < 1 or idx1 > len(blocks):
        raise IndexError(f'para {idx1} out of range {len(blocks)}')
    parts[(idx1-1)*2] = new
    return ''.join(parts)

def sub_para(text, idx1, old, new, label=''):
    cur = para_of(text, idx1)
    n = cur.count(old)
    if n != 1:
        raise SystemExit(f'[{label}] para {idx1}: old occurs {n} times: {old[:60]!r}')
    return replace_para(text, idx1, cur.replace(old, new, 1))

def backup(book, chunk):
    d = os.path.join(BASE, '歸檔', 'rere修正前', book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + '_y.txt')
    if not os.path.exists(dst):
        shutil.copy2(path_of(book, chunk), dst)
        print('backup ->', dst)
    else:
        print('backup exists ->', dst)

def save(text, book, chunk):
    with open(path_of(book, chunk), 'wb') as f:
        f.write(text.encode('utf-8'))
