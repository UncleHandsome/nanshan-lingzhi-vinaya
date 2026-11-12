# -*- coding: utf-8 -*-
"""驗證 out vs 備份：段數、行尾、相異段、二重替換檢查。用法：python _r2i_verify.py 09c_中三上 10a_中三下"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2i_lib as L

for chunk in sys.argv[1:]:
    cur = L.load_out(chunk)
    bp = os.path.join(L.BK_DIR, chunk + '_i.txt')
    b = open(bp, 'rb').read().decode('utf-8')
    eolb = '\r\n' if '\r\n' in b else '\n'
    sepb = eolb + eolb
    bp_segs = b.split(sepb)
    traili = ''
    if bp_segs and bp_segs[-1] == '':
        bp_segs = bp_segs[:-1]; traili = sepb
    elif bp_segs and bp_segs[-1].endswith(eolb):
        bp_segs[-1] = bp_segs[-1][:-len(eolb)]; traili = eolb
    diff = [i + 1 for i in range(min(len(cur['segs']), len(bp_segs))) if cur['segs'][i] != bp_segs[i]]
    same_struct = (len(cur['segs']) == len(bp_segs) and cur['eol'] == eolb and cur['trailing'] == traili)
    # 二重替換痕跡（同段出現兩次相同新詞開頭）
    print('%s: segs=%d (bak %d) eol=%r trailing=%r struct_ok=%s diff=%d %s' % (
        chunk, len(cur['segs']), len(bp_segs), cur['eol'], cur['trailing'], same_struct, len(diff), diff))
    # 檢查是否有常見殘留
    bad = []
    for i, t in enumerate(cur['segs']):
        if '  ' in t or '。。' in t or '，，' in t:
            bad.append(i + 1)
    if bad:
        print('   whitespace/double-punct segs:', bad)
