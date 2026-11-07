import io, os, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())[7]
a, b = ZI[168][0], ZI[169][0]
lines = [
    '# 篇08 記169、170 補譯提示詞', '',
    '你是律學古籍翻譯專家，專精道宣律師《行事鈔》與元照律師《資持記》。', '',
    '## 任務',
    '下列兩段《資持記》原文目前沒有白話翻譯（白話欄誤貼古文）。請逐段翻成現代白話。', '',
    '## 規則',
    '1. 一段對一段，不可合併。',
    '2. 只回 JSON：`{"記169": "白話…", "記170": "白話…"}`',
    '3. 術語保留（波羅夷、僧殘、捨戒、優婆塞、沙彌等）。',
    '4. 義理不可增減。', '',
    '## 記169 原文', a, '',
    '## 記170 原文', b, '',
    '## 回傳格式',
    '```json',
    '{"記169": "", "記170": ""}',
    '```',
]
io.open(os.path.join(B, '提示詞_篇08_記169-170.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('written', len(a), len(b))
