
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_vol.py'
s = io.open(p, encoding='utf-8').read()
old = "        out.append(dict(key=key, num=num, juan=key.split('_', 1)[1], src=sp, tr=tp))"
new = """        # 去掉開頭連續的篇目清單（與正文篇題重複）
        jp = re.compile(r'^[\\u4e00-\\u9fff]{2,10}篇第[\\u4e00-\\u9fff]+$')
        i = 0
        while i < len(sp) and not jp.match(sp[i]): i += 1
        j = i
        while j < len(sp) and jp.match(sp[j]): j += 1
        if j - i >= 3 and j < len(sp):
            del sp[i:j]
            if len(tp) > j: del tp[i:j]
            elif i < len(tp): del tp[i:]
        out.append(dict(key=key, num=num, juan=key.split('_', 1)[1], src=sp, tr=tp))"""
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
