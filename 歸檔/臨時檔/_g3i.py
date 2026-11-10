import io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
out=json.load(open("_g2out.json",encoding="utf-8"))
want={("01b_卷上之上","5"),("03b_卷中之上","23"),("04a_卷中之下","23"),("01b_卷上之上","94"),("03b_卷中之上","3")}
for ch,seg,t in out:
    if (ch,seg) in want:
        print(f"===== {ch} seg{seg}")
        print(t)
        print()
