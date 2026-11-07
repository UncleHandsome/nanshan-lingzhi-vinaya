import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
REMOVE = {16: [68, 108, 118], 17: [9, 13, 17, 48], 18: [25, 47, 103]}
for p, ns in REMOVE.items():
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇%02d.json' % p)
    if not os.path.exists(fp):
        continue
    m = json.load(io.open(fp, encoding='utf-8-sig'))
    before = len(m.get('splits', []))
    m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in ns]
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('篇%d 移除 %d 條（原 %d）' % (p, before - len(m['splits']), before))

# 生成切點驗證提示詞
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
PROP = [
    (16, 68, '第九，示法中，初科。'),
    (16, 108, '〔舊指《首疏》非。'),
    (16, 118, '〔形安心樂為二。'),
    (17, 9, '釋名中。'),
    (17, 13, '然雖互通，本制須定；'),
    (17, 17, '第二作之方法，求財中'),
    (17, 48, '《智論》明其衣體，故'),
    (18, 25, '盡形，藥體中，《僧祇'),
    (18, 47, '中間不淨，即大界也。'),
    (18, 103, '三中。'),
]
lines = ['# 切點驗證清單', '', '下面是我打算加的「記文切點」。請逐條回覆：`可用`／`改：改成哪句`／`不切`。', '',
         '格式：```json', '{', '  "16-68": "可用",', '  "17-9": "改：改到「XXX」之前",', '  "18-47": "不切"', '}', '```', '']
for p, n, mk in PROP:
    t = ZI[p - 1][n - 1][0]
    i = t.find(mk)
    head = t[:i]
    tail = t[i:]
    lines.append('## 篇%d 記%d' % (p, n))
    lines.append('- 切點：`%s`' % mk)
    lines.append('- 前半（歸上一鈔）：%s' % (head[-60:] if head else '（空）'))
    lines.append('- 後半（歸本鈔）：%s' % tail[:80])
    lines.append('')
io.open(os.path.join(B, '切點驗證_16-18.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('驗證清單已寫出')
