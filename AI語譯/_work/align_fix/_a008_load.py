# -*- coding: utf-8 -*-
"""載入 sec14 的 記/鈔 全文，存成 json 供後續比對。"""
import io, os, re, sys, json, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')
sec = SECS[13]
print('sec name', sec['name'], 'no', sec['no'], 'cand', len(sec['items']))
Z = ex.zitems_for(13, ZS)
print('zitems', len(Z))
json.dump({
    'cao': [t for t, tr in sec['items']],
    'cao_tr': [tr for t, tr in sec['items']],
    'ji': [t for t, tr in Z],
    'ji_tr': [tr for t, tr in Z],
}, io.open(os.path.join(D, '_a008_data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# sanity vs 008.json
j8 = json.load(io.open(os.path.join(D, '008.json'), encoding='utf-8'))
print('008 items', len(j8['items']), 'cand', len(j8['cand']))
ok = 0
for it in j8['items'][:5]:
    z = it['z']
    print(z, '| file:', it['text'][:40], '| src:', Z[z][0][:40])
for it in j8['items']:
    z = it['z']
    head = it['text']
    if Z[z][0][:len(head)] == head or head[:len(Z[z][0])] == Z[z][0]:
        ok += 1
print('head match', ok, '/', len(j8['items']))
okc = 0
for cd in j8['cand']:
    c = cd['c']; t = cd['text']
    if sec['items'][c][0][:len(t)] == t or t[:len(sec['items'][c][0])] == sec['items'][c][0]:
        okc += 1
print('cand head match', okc, '/', len(j8['cand']))
print('ji len chars total', sum(len(x) for x in Z))
print('cao len chars total', sum(len(t) for t, tr in sec['items']))
