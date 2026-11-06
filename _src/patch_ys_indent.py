import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
lines = io.open(p, encoding='utf-8').read().split('\n')
# 以內容定位，重寫 297-303（0 起 296..302）
start = None
for i, l in enumerate(lines):
    if l.strip() == "o = o.strip('*').lstrip()":
        start = i
        break
assert start is not None
block = [
    "            o = o.strip('*').lstrip()",
    "            o = re.sub(r'\\*+', '', o)",
    "            m3 = re.search(r'【[疏記]】', o)",
    "            if m3 and m3.start() > 0:",
    "                o = o[m3.start():]",
    "            if ytags and 0 <= gi < len(ytags) and ytags[gi] and not o.startswith('【'):",
    "                o = ytags[gi] + o",
]
# 找到原本區塊結尾（下一行是 j = i）
end = start
while end < len(lines) and lines[end].strip() != 'j = i':
    end += 1
new = lines[:start] + block + lines[end:]
io.open(p, 'w', encoding='utf-8').write('\n'.join(new))
print('block rewritten', start, end)
