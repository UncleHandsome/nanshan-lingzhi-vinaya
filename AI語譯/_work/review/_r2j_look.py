# -*- coding: utf-8 -*-
"""look.py：印出指定段中含關鍵詞的句子（譯文與原文分開）。用法：
python _r2j_look.py "chunk|seg|關鍵詞|原文關鍵詞" ...
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2j_lib as L

MAP = L.load_map()
BY = {}
for x in MAP:
    BY[(x['resp'], int(x['uniq']))] = x


def sents(s):
    return [x for x in re.split(r'(?<=[。！？；])', s) if x.strip()]


def main(args):
    cache = {}
    for a in args:
        parts = a.split('|')
        chunk, seg = parts[0], int(parts[1])
        kw = parts[2] if len(parts) > 2 else ''
        okw = parts[3] if len(parts) > 3 else ''
        if chunk not in cache:
            cache[chunk] = L.load_out(chunk)
        t = cache[chunk]['segs'][seg - 1]
        print('### %s#%d [%s]' % (chunk, seg, kw))
        hit = [x for x in sents(t) if kw in x]
        print('T:', (' … '.join(hit) if hit else t[:260]))
        if okw:
            # find orig via map by chunk+seg
            rec = None
            for x in MAP:
                if x['chunk'] == chunk and x['seg'] == seg:
                    rec = x
                    break
            if rec:
                oh = [x for x in sents(rec['orig']) if okw in x]
                print('O:', (' … '.join(oh) if oh else rec['orig'][:300]))


if __name__ == '__main__':
    main(sys.argv[1:])
