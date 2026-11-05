import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = ['批次', 'Token', '請回覆', '接續輸出', '後續提示', '承接上一', '請查收', '複製完成',
       '餵給', '純文字格式', '全篇共', '全本《四分律比丘尼鈔》']


def clean(path):
    ls = io.open(path, encoding='utf-8').read().split('\n')
    # 1) 移除誤插的他書區塊：04 檔中「承接上一批次」到「請查收」整段
    s = next((i for i, x in enumerate(ls) if '承接上一' in x), None)
    e = next((i for i, x in enumerate(ls) if '請查收' in x), None)
    removed_block = 0
    if s is not None and e is not None and e > s:
        removed_block = e - s + 1
        ls = ls[:s] + ls[e + 1:]
    # 2) 移除提示行
    out = [x for x in ls if not any(k in x for k in KEY)]
    removed_lines = len(ls) - len(out)
    # 3) 收斂連續空白行
    res = []
    for x in out:
        if x.strip() == '' and res and res[-1].strip() == '':
            continue
        res.append(x)
    io.open(path, 'w', encoding='utf-8').write('\n'.join(res).rstrip('\n') + '\n')
    return removed_block, removed_lines, len(res)


for f in ['04_四分律比丘尼鈔_句讀_clean.txt', '05_四分律拾毗尼義鈔_句讀_clean.txt']:
    print(f, clean(os.path.join(B, f)))
