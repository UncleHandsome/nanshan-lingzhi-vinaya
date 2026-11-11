# -*- coding: utf-8 -*-
"""套用一批 edits（JSON 檔）：[{chunk,seg,old,new,why,resp}, ...]
同 chunk 先讀現行、逐段替換、寫回；首次備份 _f。日誌追加 _r2z4_log.jsonl。
"""
import sys, os, json
from _r2z4_lib import apply_edits, OUT_DIR

def main(path):
    edits = json.load(open(path, encoding='utf-8'))
    by_chunk = {}
    for e in edits:
        by_chunk.setdefault(e['chunk'], []).append(e)
    total = 0
    for chunk, es in by_chunk.items():
        log = apply_edits(chunk, es, note=os.path.basename(path))
        total += len(log)
        with open('_r2z4_log.jsonl', 'a', encoding='utf-8') as f:
            for r in log:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print('OK', chunk, len(log))
    print('TOTAL', total)

if __name__ == '__main__':
    main(sys.argv[1])
