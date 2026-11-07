import io, os, glob
from docx import Document
import importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

def jt(p, n):
    return ZI[p - 1][n - 1][0] if n <= len(ZI[p - 1]) else ''

def chao(p, nums):
    f = glob.glob(B + r'\白話\會本_篇%02d_*.docx' % p)[0]
    ps = [x.text.strip() for x in Document(f).paragraphs]
    out = {}
    for k in nums:
        key = '【鈔%d】' % k
        for t in ps:
            if t.startswith(key):
                out[k] = t[len(key):]
                break
    return out

L = ['你是《四分律行事鈔資持記》會本的編輯助手，熟悉道宣律師《行事鈔》與元照律師《資持記》的科判。', '',
     '## 背景',
     '會本體例：【鈔】原文 → 白話 →【記】註解 → 白話。',
     '問題：有些【記】一條註解跨了好幾條鈔，卻被排在其中一條鈔之後，導致「記文回釋前面的鈔」。', '',
     '## 任務',
     '下面每條問題都附「鈔文」與「記文」。請告訴我這條記要切成幾段、每段切在什麼字之前、各段應歸哪一條鈔。', '',
     '### 輸出格式（只回 JSON）',
     '```json',
     '{',
     '  "30-011": {',
     '    "段": [',
     '      {"切在": "XXX", "歸鈔": 4},',
     '      {"切在": "YYY", "歸鈔": 5},',
     '      {"歸鈔": 6}',
     '    ]',
     '  }',
     '}',
     '```', '',
     '（最後一段不用給「切在」，只給「歸鈔」。若整條不需切，回 `{"30-011": {"整條歸鈔": 4}}`。）', '',
     '---', '']

# 篇30
c30 = chao(30, list(range(1, 24)))
L += ['# 一、篇30 諸部別行', '', '## 鈔文', '']
for k in sorted(c30):
    L.append('【鈔%d】%s' % (k, c30[k][:160]))
L.append('')
for n, note in [(6, '記006 開頭「淨地，則《四分》用廢教為寬…」其實在釋鈔01 末尾，鈔02 卻插在中間'),
                (11, '記011 一次囊括鈔04、鈔05、鈔06'),
                (16, '記016 開頭「同名有重，故還三重…」在釋鈔07，卻排在鈔10 後'),
                (19, '記019 跨鈔13、14、15、16、17')]:
    L += ['## 篇30 記%03d' % n, '問題：%s' % note, '', '記文：', '', jt(30, n), '']

# 篇5
c5 = chao(5, [33, 34, 35])
L += ['# 二、篇5 通辨羯磨（鈔33/34/35）', '']
for k in sorted(c5):
    L.append('【鈔%d】%s' % (k, c5[k][:160]))
L.append('')
for n in (80, 81):
    L += ['## 篇5 記%03d' % n, '', jt(5, n), '']

# 篇8
c8 = chao(8, [31])
L += ['# 三、篇8 受戒緣集（鈔31 切斷三障句）', '', '【鈔31】%s' % c8.get(31, '')[:200], '']
for n in (108, 109):
    L += ['## 篇8 記%03d' % n, '', jt(8, n), '']

# 篇7
L += ['# 四、篇7 僧網大綱', '']
for n, note in [(17, '前半譯文缺尾，《涅槃》段開頭是前半翻譯'), (23, '「舍衛」被 OCR 成缺字')]:
    L += ['## 篇7 記%03d' % n, '問題：%s' % note, '', jt(7, n), '']

# 篇27 記041
L += ['# 五、篇27 記041（三段歸鈔40/41/42，請複驗）', '', jt(27, 41), '',
      '## 篇27 鈔40/41/42', '']
c27 = chao(27, [40, 41, 42])
for k in sorted(c27):
    L.append('【鈔%d】%s' % (k, c27[k][:140]))
L += ['', '請回：這段切法是否正確？若不對，給正確切點。']

io.open(os.path.join(B, '提示詞_多段切分_第五批.md'), 'w', encoding='utf-8').write('\n'.join(L))
print('len', len('\n'.join(L)))
