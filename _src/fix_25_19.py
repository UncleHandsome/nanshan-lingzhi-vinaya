import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 1) 篇25 記003 譯文修正
fp = os.path.join(B, 'AI語譯', 'out', '資持記', '15e_下三.txt')
s = io.open(fp, encoding='utf-8').read()
old = '引《五分律》。睡覺時不得裸露而眠，是為了防止發生突發災難時有失威儀。'
new = '引《五分律》：不可同床共眠，是為了防範危難與譏嫌的緣故。'
if old in s:
    io.open(fp, 'w', encoding='utf-8').write(s.replace(old, new))
    print('篇25 記003 譯文已改')
else:
    print('篇25 找不到字串')

# 2) 篇19 切點：記005 尾段歸鈔05；記016 前半歸鈔07
mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇19.json')
m = json.load(io.open(mp, encoding='utf-8-sig')) if os.path.exists(mp) else {'splits': []}
add = [
    {'n': 5, 'base': 4, 'markers': ['明體中，初科'], 'targets': [4, 5]},
    {'n': 16, 'base': 7, 'markers': ['加受中二，前引'], 'targets': [7, 8]},
]
nums = {e['n'] for e in add}
m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums] + add
json.dump(m, io.open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇19 切點已寫入')
