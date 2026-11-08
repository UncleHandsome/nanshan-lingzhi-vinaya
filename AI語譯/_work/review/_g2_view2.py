import io
for l in io.open('AI語譯/_work/review/fix_re2_g2.tsv',encoding='utf-8'):
    f=l.rstrip('\n').split('\t')
    if len(f)==4 and ((f[1]=='04b_卷上之四' and f[2] in ('2','5')) or (f[1]=='04a_卷上之四' and f[2]=='13')):
        print('===',f[1],f[2]); print(f[3]); print()
