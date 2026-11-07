import io, os, re, glob, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

def ex_(t, n=200):
    t = re.sub(r'\s+', '', t)
    return t if len(t) <= n else t[:n] + '……' + t[-50:]

# 找 篇26 法師段
found = ''
for f in glob.glob(os.path.join(B, 'TXT_分卷', '01_行事鈔', '*.txt')):
    s = io.open(f, encoding='utf-8').read().replace('\n', '')
    i = s.find('若法師者云')
    if i >= 0:
        found = s[i:i + 500]
        break

# 找 後跋
ba = ''
for f in glob.glob(os.path.join(B, 'TXT_分卷', '01_行事鈔', '*.txt')):
    s = io.open(f, encoding='utf-8').read().replace('\n', '')
    i = s.find('武德九年')
    if i >= 0:
        ba = s[max(0, i - 60):i + 260]
        break

CUTS = [(3, 24), (3, 25), (3, 26), (4, 50), (4, 52), (5, 70), (5, 71), (5, 78), (5, 79), (5, 80),
        (7, 7), (7, 8), (8, 122), (8, 123), (8, 124), (14, 44), (16, 67), (16, 68), (17, 179), (18, 98), (22, 68)]

L = ['# 會本：待補譯與待修正（含原文，可離線作業）', '', '更新：2026-11-07（第八版）', '',
     '每項都附原文與前後段落，直接在本檔回覆即可。', '',
     '## 一、需要補譯（3 段）', '',
     '### 1. 篇26 鈔07（法師／禪師段）', '', '原文（節錄）：', '', found or '（未找到）', '',
     '現況：白話欄照抄古文，需整段白話。', '',
     '### 2. 篇10 記035（後半）', '', '原文：', '', ZI[9][34][0], '',
     '現況：白話欄照抄古文，需整段白話。', '',
     '### 3. 篇30 後跋【鈔】原文', '',
     '底本線索（跋文開頭附近）：', '', ba or '（未找到「武德九年」字樣）', '',
     '需要：跋文原文，或告訴我從哪個底本抓。', '',
     '## 二、需要切點（回「切在『XXX』之前」）', '']

for p, n in CUTS:
    if n > len(ZI[p - 1]):
        continue
    t = ZI[p - 1][n - 1][0]
    L += ['### 篇%d 記%03d' % (p, n), '',
          '- 開頭：%s' % ex_(t, 180), '',
          '- 結尾：%s' % ex_(t[-180:], 180), '']

t450 = ZI[0][-1][0]
L += ['### 篇1 記（最後一條，混入篇2 開頭）', '', '- 開頭：%s' % ex_(t450, 150), '',
      '- 結尾：%s' % ex_(t450[-220:], 220), '']

L += ['## 三、需要確認', '',
      '- 篇16 鈔59 衍文（重複句）要不要刪？',
      '- 篇14 的 19 個切點已套用， AI 原 148 條已捨棄，是否保留部分？', '',
      '## 四、回覆格式', '',
      '```json',
      '{',
      '  "篇26_鈔07": "白話…",',
      '  "篇10_記035": "白話…",',
      '  "3-24": "切在「XXX」之前",',
      '  "16-68": "整條歸記067",',
      '  "篇16_鈔59衍文": "刪",',
      '}',
      '```']

io.open(os.path.join(B, '待補譯與修正_彙總.md'), 'w', encoding='utf-8').write('\n'.join(L))
print('done', len('\n'.join(L)))
