import io, json, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
mine = json.load(io.open(os.path.join(AD, 'out_001.json'), encoding='utf-8'))['map']
prop = json.load(io.open(os.path.join(B, '_tmp_a2prop.json'), encoding='utf-8'))['clamped']
a = [(x['z'], x['c']) for x in mine]
b = [(int(z), int(c)) for z, c in prop]
print('identical to independently computed length-proportional map:', a == b)
print('n', len(a), 'monotone', all(a[i][1] <= a[i+1][1] for i in range(len(a)-1)))
print('z contiguous', [z for z, c in a] == list(range(300, 450)))
