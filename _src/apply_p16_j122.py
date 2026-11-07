import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
fp = os.path.join(B, 'AI語譯', 'out', '資持記', '12b_中四下.txt')
NEW = ("必須知道，只要蓄積之心已經斷除，當天就可以返還；如果心中仍存有蓄積的貪心，即使過了多日也同樣會沾染罪過。"
       "鈔文指陳破除偏執、轉而又依舊採用的做法，用意在於使兩者圓通無礙；鈔文所指的上方論文，就是《多論》的第一句。"
       "「今且」以下的文句，是採取古舊之法。在五種長物中，長藥是當天立即返還，正如上面《戒疏》所說。"
       "在還法中，第一段文字是先引述律中的開緣。")
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
for i, t in enumerate(tt):
    if t.startswith('須知心斷，當日可還'):
        k = t.find('大眾眾多')
        tail = t[k:] if k > 0 else ''
        tt[i] = NEW + tail
        io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
        print('已修 第', i + 1, '段；原長', len(t), '新長', len(tt[i]))
        break
else:
    print('找不到')
