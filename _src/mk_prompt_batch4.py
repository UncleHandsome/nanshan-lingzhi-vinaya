import io, os, re, glob
from docx import Document
import importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

def jtext(p, n):
    return ZI[p - 1][n - 1][0] if n <= len(ZI[p - 1]) else ''

def chao_from_docx(p, keys):
    f = glob.glob(B + r'\白話\會本_篇%02d_*.docx' % p)[0]
    ps = [x.text.strip() for x in Document(f).paragraphs]
    out = {}
    for k in keys:
        key = '【鈔%d】' % k
        for t in ps:
            if t.startswith(key):
                out[k] = t[len(key):]
                break
    return out

L = ['你是《四分律行事鈔資持記》會本的編輯助手，熟悉道宣律師《行事鈔》與元照律師《資持記》的科判。', '',
     '## 任務一：補譯（4 句，篇7）', '會本白話欄直接貼了古文，請翻成白話（術語保留）。', '',
     '1. 鈔06 後半：若善比丘置不訶責，當知是人佛法中怨；若能驅遣舉處治罰，是我弟子真聲聞也。',
     '2. 鈔07 後半：自非治罰，何由可息？如似遲驢，必加楚罰；則有七種調伏，及惡馬治、默擯、不與語等。',
     '3. 鈔08 後半：有過之徒，實當此罰；反用俗法…準而行之。',
     '4. 鈔09 後半：具如律本遮法中說。若違上法…亦滅正法。', '',
     '## 任務二：切點（篇7、篇8）', '請回「切在『XXX』之前」或「整條搬到鈔NN 之後」或「不確定」。', '']

for p, n, note in [(7, 7, '前半譯文多出「化教，標中」句，應歸後半'),
                   (7, 17, '前半譯文缺尾，《涅槃》段開頭是前半翻譯'),
                   (7, 31, '（中）譯文被擠到（後）'),
                   (8, 39, '標籤把「木叉」切斷（記038 尾「復有五法〔不具持木」，記039 從「叉」起）'),
                   (8, 42, '前半譯文缺，部分被搬到後半'),
                   (8, 43, '古文脫字：「高德重」／「意取高」')]:
    L += ['### 篇%d 記%03d' % (p, n), '問題：%s' % note, '', '記文：', '', jtext(p, n), '']

L += ['## 任務三：篇14 單提 52–60 戒（鈔223–231）', '',
      '會本中記文連鎖滯後（鈔223 後記951 只寫「五十二」，其後記952 才回頭釋52戒）。',
      '請指出「每條鈔之後應接哪幾條記」。', '']
c14 = chao_from_docx(14, list(range(223, 232)))
for k in range(223, 232):
    L.append('【鈔%d】%s' % (k, c14.get(k, '')[:110]))
L += ['', '記文（951–981）開頭：', '']
for n in range(951, 982):
    t = jtext(14, n)
    if t:
        L.append('記%03d：%s' % (n, t[:70]))

L += ['', '## 任務四：篇1 記449、篇30 記001、篇27 記041', '',
      '這三條需要多次切分或整條搬移，請給具體做法。', '',
      '### 篇1 記448 / 449 / 450（鈔15、鈔16 之間）', '',
      jtext(1, 448), '', '記449：', jtext(1, 449), '', '記450：', jtext(1, 450), '',
      '### 篇30 記001（前有篇29 記055 殘文）', '', jtext(30, 1), '',
      '### 篇27 記041（跨鈔40/41/42）', '', jtext(27, 41), '',
      '## 輸出格式（只回 JSON）', '```json', '{',
      '  "篇7_鈔06後半": "白話…",',
      '  "7-007": {"修法": "切在「XXX」之前"},',
      '  "14-排序": {"鈔223": "記951", "鈔224": "記952"},',
      '  "1-449": {"修法": "切在「XXX」之前"},',
      '  "8-039": {"修法": "整條搬到記038 之後"}', '}', '```']

io.open(os.path.join(B, '提示詞_剩餘_第四批.md'), 'w', encoding='utf-8').write('\n'.join(L))
print('len', len('\n'.join(L)))
