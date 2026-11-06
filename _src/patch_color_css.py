import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\docs\style.css'
c = io.open(p, encoding='utf-8').read()
add = """
/* 【疏】【記】分色（業疏、戒疏） */
.pair .o.ji{background:#eef2f6;border-left:3px solid #5b8bb0;color:#1f3f5c}
.pair .o.shu{background:#f4efe2;border-left:3px solid #a98b4f;color:#4a3b22}
"""
if '.pair .o.ji' not in c:
    io.open(p, 'a', encoding='utf-8').write(add)
    print('css added')
else:
    print('already')
