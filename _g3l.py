import io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
out=dict(((ch,seg),t) for ch,seg,t in json.load(open("_g2out.json",encoding="utf-8")))
t=out[("03b_卷中之上","21")]
i=t.find("這不同於僧物")
print("SEG21a:", t[i-60:i+230])
print()
j=t.find("施主是以深重信心")
print("SEG21b:", t[j-60:j+90])
print()
t2=out[("03b_卷中之上","32")]
k=t2.find("如果依據此項標準")
print("SEG32:", t2[k-60:k+80])
print()
t3=out[("02a_卷上之下","16")]
m=t3.find("第四、")
print("SEG16:", t3[m-40:m+90])
