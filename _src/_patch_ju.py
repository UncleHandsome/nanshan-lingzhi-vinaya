# -*- coding: utf-8 -*-
"""把 site_ju.py 內硬編碼的 句讀_clean.txt 路徑改為 _ju_path()，可在根目錄或歸檔/臨時檔找。"""
import io, os, re

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_src', 'site_ju.py')
s = io.open(P, encoding='utf-8').read()

HELPER = '''def _ju_path(B, name):
    """句讀_clean 檔可能被歸檔到 歸檔/臨時檔/，兩處都找。"""
    for rel in ('', os.path.join('歸檔', '臨時檔')):
        p = os.path.join(B, rel, name) if rel else os.path.join(B, name)
        if os.path.exists(p):
            return p
    return os.path.join(B, name)

'''

if '_ju_path(' not in s:
    s = re.sub(r"os\.path\.join\(B, '([0-9]{2}_[^']+_句讀_clean\.txt)'\)",
               lambda m: "_ju_path(B, '%s')" % m.group(1), s)
    # 插入 helper：放在第一個 def 之前
    m = re.search(r'(?m)^def ', s)
    if m:
        s = s[:m.start()] + HELPER + s[m.start():]
    else:
        s = HELPER + s
    io.open(P, 'w', encoding='utf-8').write(s)
    print('patched')
else:
    print('already patched')
