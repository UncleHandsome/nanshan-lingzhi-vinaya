import importlib.util, os, io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

lines = ['# 會本待補／待重查清單', '']
def add(title, src, note):
    lines.append('## ' + title)
    lines.append('- 原文：%s' % src)
    lines.append('- 需求：%s' % note)
    lines.append('')

# 篇23 記58 末兩句
z23 = ZI[22]
t = z23[57][0]
lines.append('## 1. 篇23 記058 末兩句（缺譯）')
lines.append('- 原文：次科。引經佛在說法，令後倣之。晡即申時。')
lines.append('- 所在記文末段：%s' % t[-60:])
lines.append('- 需求：補這兩句的白話（現有譯文到「消受他人的信施供養呢？」為止）')
lines.append('')

# 篇21 記16、42
z21 = ZI[20]
for n, key in ((16, '出要，即證理'), (42, '崇，猶重也')):
    t = z21[n - 1][0]
    i = t.find(key)
    lines.append('## 篇21 記%03d（譯文位移）' % n)
    lines.append('- 原文片段：%s' % t[max(0, i - 40):i + 40])
    lines.append('- 需求：確認「%s」的譯文應在前半結尾，現落在後半開頭' % key)
    lines.append('')

# 篇19 記23 重複
z19 = ZI[18]
t = z19[22][0]
cnt = t.count('初文《四分》七段')
lines.append('## 篇19 記023（重複句）')
lines.append('- 「初文《四分》七段」在原記出現 %d 次' % cnt)
lines.append('- 原文末段：%s' % t[-80:])
lines.append('- 需求：確認是否底本重複；若只有一次，切點應改到第二次出現處')
lines.append('')

io.open(os.path.join(B, '會本待補清單.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
