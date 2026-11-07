import io, os, importlib.util, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('hb', os.path.join(B, '_src', 'hebian_ju.py'))
hb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hb)
for idx, zi, anchors, front in hb.PLAN[:2]:
    sec = hb.secs[idx]
    vols = collections.Counter(v for o, t, v, *_ in sec['items'])
    print('篇', idx + 1, sec['name'], '鈔段', len(sec['items']), '卷分布', dict(vols))
    print('  記段', len(zi), 'front', len(front), 'anchors keys', sorted(anchors)[:6])
