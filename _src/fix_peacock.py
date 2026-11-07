import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
fp = os.path.join(B, 'AI語譯', 'out', '資持記', '14b_下二.txt')
s = io.open(fp, encoding='utf-8').read()
old1 = '「亂雀咽」就是取麻雀咽喉部位羽毛的雜色'
new1 = '「孔雀咽」就是取孔雀頸部羽毛的青翠色'
if old1 in s:
    s = s.replace(old1, new1)
    io.open(fp, 'w', encoding='utf-8').write(s)
    print('已修正 亂雀 → 孔雀')
else:
    print('找不到字串，檢查：', '亂雀' in s)
