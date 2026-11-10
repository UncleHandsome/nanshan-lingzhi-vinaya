import io
p = r"AI語譯/out/01_行事鈔/01b_卷上之一.txt"
ps = [s for s in io.open(p, encoding="utf-8").read().split("\n") if s.strip()]
print("total paras:", len(ps))
for i in range(55, 86):
    print(i+1, ps[i][:60].replace("\n"," "))
