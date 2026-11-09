p="tmp_build.py"
s=open(p,encoding="utf-8").read()
old=s[s.index("# diff report"):]
new='''# diff report
out = []
for (book, chunk, seg, new) in rows:
    i = next(idx for idx in applied if data[idx][0] == [book, chunk, seg])
    cur = data[i][1][0]["current"].replace("\\n", "")
    sm = difflib.SequenceMatcher(None, cur, new, autojunk=False)
    out.append(f"===== {i} | {book} | {chunk} | seg {seg}")
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        out.append(f"  [{tag}] -{cur[max(0,i1-25):i2+25]!r}")
        out.append(f"          +{new[max(0,j1-25):j2+25]!r}")
open("AI語譯/_work/review/tmp_re8/diff.txt", "w", encoding="utf-8").write("\\n".join(out))
print("diff lines:", len(out))
'''
s=s.replace(old,new)
open(p,"w",encoding="utf-8").write(s)
