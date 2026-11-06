# -*- coding: utf-8 -*-
"""Build & validate out_016.json for batch 016 (z150-z240)."""
import io, os, re, json, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS, ZS = ex.sections(), ex.zsecs()
SKIP1 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2 = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')
IDX = 14
C = [o for o, t in SECS[IDX]['items'] if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
Z = ex.zitems_for(IDX, ZS)
J = json.load(io.open(os.path.join(AD, '016.json'), encoding='utf-8'))

# z -> c assignments (manual, from full-text comparison)
A = {
    150: 60, 151: 60, 152: 60, 153: 60,
    154: 61, 155: 61, 156: 61,
    157: 62, 158: 62, 159: 62, 160: 62,
    161: 63,
    162: 64, 163: 64,
    164: 65, 165: 65,
    166: 66,
    167: 68, 168: 68,
    169: 69, 170: 69, 171: 69, 172: 69, 173: 69,
    174: 70, 175: 70, 176: 70, 177: 70,
    178: 71,
    179: 72,
    180: 75,
    181: 76, 182: 76, 183: 76, 184: 76, 185: 76,
    186: 76, 187: 76, 188: 76, 189: 76, 190: 76,
    191: 77, 192: 77, 193: 77, 194: 77, 195: 77, 196: 77, 197: 77,
    198: 77, 199: 77, 200: 77, 201: 77, 202: 77, 203: 77, 204: 77,
    205: 78, 206: 78, 207: 78, 208: 78, 209: 78, 210: 78,
    211: 79,
    212: 80, 213: 80,
    214: 81, 215: 81,
    216: 82, 217: 82, 218: 82, 219: 82,
    220: 83,
    221: 84,
    222: 85,
    223: 86, 224: 86, 225: 86,
    226: 87,
    227: 88, 228: 88, 229: 88,
    230: 89,
    231: 90,
    232: 91,
    233: 92, 234: 92, 235: 92, 236: 92, 237: 92, 238: 92, 239: 92, 240: 92,
}

items = J['items']
zs = [it['z'] for it in items]
assert zs == list(range(150, 241)), zs
assert set(A) == set(zs), (len(A), len(zs))

out = {'map': [{'z': z, 'c': A[z]} for z in zs]}
io.open(os.path.join(AD, 'out_016.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, ensure_ascii=False, separators=(',', ':')))

# validation
cs = [A[z] for z in zs]
print('items', len(zs), 'cand', len(J['cand']))
print('range ok', min(cs) >= 0 and max(cs) < len(J['cand']))
print('monotonic', all(cs[i] <= cs[i+1] for i in range(len(cs)-1)))
print('distinct c used', len(set(cs)))
print('per-c counts', sorted({c: cs.count(c) for c in set(cs)}.items()))
print('written out_016.json')

# anchor check: does the 牒詞 vocabulary of z overlap with the assigned c?
def bigrams(s):
    s = ''.join(re.findall(r'[\u4e00-\u9fff]', s))
    return {s[i:i+2] for i in range(len(s)-1)}

for z in zs:
    c = A[z]
    zt = dict((it['z'], it['text']) for it in items)[z]
    bz = bigrams(zt)
    best = max(range(len(C)), key=lambda k: len(bigrams(C[k]) & bz))
    mark = '' if best == c else '  <-- best c%d (score %d) vs c%d (score %d)' % (
        best, len(bigrams(C[best]) & bz), c, len(bigrams(C[c]) & bz))
    print('z%d c%d%s' % (z, c, mark))
