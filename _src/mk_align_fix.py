# -*- coding: utf-8 -*-
"""重建 篇9-27 的對齊批次（用正確的記文分節）"""
import io, os, re, json, importlib.util, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', '_work', 'align_fix')
BLOCK = 150

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections()
ZS = ex.zsecs()
SKIP1 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2 = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    n = 0
    for idx in range(8, 27):          # 篇9-27（0-based 8..26）
        C = [o for o, t in SECS[idx]['items']
             if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
        Z = ex.zitems_for(idx, ZS)
        if not C or not Z:
            continue
        for s in range(0, len(Z), BLOCK):
            n += 1
            blk = Z[s:s + BLOCK]
            io.open(os.path.join(OUT, '%03d.json' % n), 'w', encoding='utf-8').write(json.dumps(dict(
                sec=idx + 1, name=SECS[idx]['name'],
                items=[dict(z=s + i, text=o[:90]) for i, (o, t) in enumerate(blk)],
                cand=[dict(c=c, text=o[:90]) for c, o in enumerate(C)]), ensure_ascii=False, indent=1))
            print('批次%03d 篇%-3d %-6s 記%3d-%3d 鈔%3d' % (n, idx + 1, SECS[idx]['name'], s, s + len(blk) - 1, len(C)))
    print('batches', n)


if __name__ == '__main__':
    main()
