# -*- coding: utf-8 -*-
"""把 patch_r2_01a.py / patch_r2_01b.py 的修正套用到 AI語譯/out/01_行事鈔/<chunk>.txt

用法：
    python -X utf8 AI語譯/_work/review/apply_r2_01.py 01a [--dry]
"""
import io, os, re, sys, importlib.util

B = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLK = re.compile(r'(?s)(?:(?!\r?\n\r?\n).)+')


def load(name):
    p = os.path.join(B, '_work', 'review', name)
    spec = importlib.util.spec_from_file_location(name[:-3], p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    which = sys.argv[1]
    dry = '--dry' in sys.argv
    mod = load('patch_r2_%s.py' % which)
    CH = mod.CH
    path = os.path.join(B, 'out', '01_行事鈔', CH + '.txt')
    txt = io.open(path, encoding='utf-8', newline='').read()
    spans = [m.span() for m in BLK.finditer(txt)]
    print('chunk %s：%d 個段落' % (CH, len(spans)))
    if len(spans) < 1:
        return 1

    off = 0  # 累計位移
    edited = {}
    errs = []
    # 依段落順序處理，先套 snippet 再整段替換
    per = {}
    for op in mod.OPS:
        per.setdefault(op[1], []).append(op)

    for seg in sorted(per):
        s, e = spans[seg - 1]
        b = txt[s + off:e + off]
        orig = b
        pre = re.match(r'\s*', b).group(0)   # 段落前的換行屬於本段，替換時保留
        for op in per[seg]:
            if op[0] == 'S':
                _, _, old, new = op
                n = b.count(old)
                if n != 1:
                    errs.append('seg %d: 找到 %d 次：%r' % (seg, n, old[:40]))
                    continue
                b = b.replace(old, new, 1)
            else:
                b = pre + op[2]
        if b != orig:
            nl = '\r\n' if '\r\n' in txt else '\n'
            b = b.replace('\r\n', '\n').replace('\n', nl)
            edited[seg] = (orig, b)

    if errs:
        print('有 %d 個 snippet 對不上，未寫檔：' % len(errs))
        for x in errs:
            print('  ', x)
        return 1

    out = []
    last = 0
    for seg in sorted(edited):
        s, e = spans[seg - 1]
        out.append(txt[last:s])
        out.append(edited[seg][1])
        last = e
    out.append(txt[last:])
    new_txt = ''.join(out)

    print('改動 %d 段：%s' % (len(edited), ','.join(str(x) for x in sorted(edited))))
    print('CR count: in=%d out=%d' % (txt.count('\r'), new_txt.count('\r')))
    bad = [seg for seg, (o, n) in edited.items() if not n.strip()]
    if bad:
        print('警告：以下段落改後為空', bad)
    if not dry:
        io.open(path, 'w', encoding='utf-8', newline='').write(new_txt)
        print('已寫入', path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
