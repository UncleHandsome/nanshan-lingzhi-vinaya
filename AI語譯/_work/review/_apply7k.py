# -*- coding: utf-8 -*-
"""7K 落改工具：依 chunk+段號，對 AI語譯/out 的指定段落做字串替換。
用法: python _apply7k.py edits.json
edits.json: [{"chunk":"02a_卷一之二","seg":5,"old":"...","new":"..."}, ...]
驗證：old 在該段必須恰好出現 1 次，否則報錯不寫。
行尾：保持原檔 CRLF。
"""
import json, sys, io, os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(BASE, 'AI語譯', 'out', '03_業疏')

def load(chunk):
    p = os.path.join(OUT, chunk + '.txt')
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        data = f.read()
    return p, data

def main():
    with io.open(sys.argv[1], 'r', encoding='utf-8') as f:
        edits = json.load(f)
    files = {}
    errors = []
    for e in edits:
        chunk = e['chunk']; seg = int(e['seg'])
        if chunk not in files:
            files[chunk] = load(chunk)
        p, data = files[chunk]
        lines = data.split('\r\n')
        idx = 2 * seg - 2
        if idx >= len(lines):
            errors.append('seg out of range: %s#%d' % (chunk, seg)); continue
        line = lines[idx]
        c = line.count(e['old'])
        if c != 1:
            errors.append('COUNT %d for %s#%d old=%r' % (c, chunk, seg, e['old'][:40])); continue
        lines[idx] = line.replace(e['old'], e['new'], 1)
        files[chunk] = (p, '\r\n'.join(lines))
        if c == 1:
            print('OK %s#%d  -%s +%s' % (chunk, seg, e['old'][:24], e['new'][:24]))
    if errors:
        print('ERRORS:')
        for x in errors:
            print('  ' + x)
        sys.exit(1)
    for chunk, (p, data) in files.items():
        with io.open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(data)
        print('WROTE ' + p)

main()