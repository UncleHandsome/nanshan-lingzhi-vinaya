import io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
p=r"AI語譯\_work\review\fix_re8_g2.tsv"
data=[l for l in io.open(p,encoding="utf-8").read().split("\n") if l.strip()]
d={(f[1],f[2]):f[3] for f in (l.split("\t") for l in data)}
print("first:", data[0][:60])
print("last :", data[-1][:60])
for k in [("01a_卷上之上","22"),("01a_卷上之上","35"),("03a_卷中之上","74"),("03b_卷中之上","32"),("04a_卷中之下","33"),("04b_卷中之下","19")]:
    print(k, "in file" if k in d else "ABSENT")
t=d[("01a_卷上之上","22")]
print("seg22 keeps applied fix:", "有人陳說委託欲意後" in t, "| has row14 fix:", "往往極易產生差錯" in t, "| old text gone:", "必須小心容納之間的差錯" not in t)
print("count:", len(data))
