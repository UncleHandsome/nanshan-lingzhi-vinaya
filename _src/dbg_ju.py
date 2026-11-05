import sys, io, os, re, bisect, collections
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src')
import ju_build as J

tag = sys.argv[1] if len(sys.argv) > 1 else '03_業疏'
sd, tt, ju = J.BOOKS[tag]
lines, trs, keys = J.load_trs(tag, sd, tt)
src_h, ls, le = J.ranges(lines)
raw = io.open(ju, encoding='utf-8').read()
paras = [p.strip() for p in re.split(r'\n\s*\n', raw) if p.strip()]
ju_h, ps, pe = J.ranges(paras)
anc = J.anchors(ju_h, src_h)
print(tag, 'src lines', len(lines), 'ju paras', len(paras), 'anchors', len(anc),
      'ju chars', len(ju_h), 'src chars', len(src_h))
print('first anchors', anc[:5])
print('last anchors', anc[-3:])
