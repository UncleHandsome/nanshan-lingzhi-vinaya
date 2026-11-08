import io
want={('05c_卷中之一','3'),('05c_卷中之一','4'),('05c_卷中之一','9'),('05c_卷中之一','18'),('06b_卷中之二','12'),('06b_卷中之二','28'),('06c_卷中之二','2'),('05b_卷中之一','19')}
seen=set()
for l in io.open('AI語譯/_work/review/fix_re2_g2.tsv',encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)==4 and (f[1],f[2]) in want and (f[1],f[2]) not in seen:
        seen.add((f[1],f[2])); print('===',f[1],f[2]); print(f[3]); print()
