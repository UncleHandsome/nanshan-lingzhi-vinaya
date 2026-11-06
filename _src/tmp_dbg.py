import io, os, re, bisect

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀': '床', '説': '說', '衆': '眾', '爲': '為', '敎': '教', '卽': '即', '旣': '既', '竝': '並', '収': '收', '煑': '煮', '査': '查'}
han = lambda c: '\u4e00' <= c <= '\u9fff' or c == '〇'
nh = lambda c: VAR.get(c, c)
hs = lambda s: ''.join(nh(c) for c in s if han(c)) if False else ''.join(nh(c) for c in s if han(c))
