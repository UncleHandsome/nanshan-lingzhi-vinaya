
import io
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_book.py'
s = io.open(p, encoding='utf-8').read()
old = """if __name__ == '__main__':
    book = sys.argv[1]; title = sys.argv[2]; prefix = sys.argv[3]
    chunks = load(book)
    for mode, label in (('dui', '白話對照本'), ('qian', '全白話本')):
        path = os.path.join(BASE, '白話', '%s_%s.docx' % (prefix, label))
        n = build(chunks, mode, title, path)
        print(mode, len(chunks), 'chunks', n, 'paras')"""
new = """if __name__ == '__main__':
    book = sys.argv[1]; title = sys.argv[2]; prefix = sys.argv[3]
    chunks = load(book)
    groups = {}
    for c in chunks:
        j = c['juan'].split('之')[0] if c['juan'] else '全'
        groups.setdefault(j, []).append(c)
    order = sorted(groups.keys())
    for mode, label in (('dui', '白話對照本'), ('qian', '全白話本')):
        for j in order:
            sub = groups[j]
            nm = prefix if j == '全' else '%s_%s' % (prefix, j)
            path = os.path.join(BASE, '白話', '%s_%s.docx' % (nm, label))
            n = build(sub, mode, title + ('　' + j if j != '全' else ''), path, single=True)
            print(mode, j, len(sub), 'chunks', n, 'paras')"""
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace("def build(chunks, mode, title, path):", "def build(chunks, mode, title, path, single=False):")
s = s.replace("""        if c['juan'] and c['juan'] != prev:""", """        if (not single) and c['juan'] and c['juan'] != prev:""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
