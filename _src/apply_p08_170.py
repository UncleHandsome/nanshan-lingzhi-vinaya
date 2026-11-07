import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
fp = os.path.join(B, 'AI語譯', 'out', '資持記', '04c_上三.txt')
T170 = ("（若說：）「我作優婆塞」、「我作沙彌」〔這就是漸捨。〕；捨戒必須面對比丘而捨，只要宣說一遍即可成就。"
        "《薩婆多論》所謂受戒如同採集珍寶，又如同攀登高山，必定需要依憑眾多因緣與諸多力量；捨戒則如同喪失財物，如同從高處墜落，不需要依憑眾多因緣，因此只要宣說一遍。"
        "《行事鈔》引《增一阿含經》以下，是說明捨戒再受的限度界限。該經記載因為僧伽摩比丘七次降魔，後來再次受具足戒而證得阿羅漢果，佛陀因此開許最多可以七次，七次之外便不再聽許。"
        "在比丘尼捨戒這部分中，則是引用律文來指示說明。")
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
done = False
for i, t in enumerate(tt):
    if t.startswith('云無更受者'):
        tt[i] = T170
        done = True
        print('替換第', i + 1, '段')
        break
if done:
    io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
else:
    print('找不到')
