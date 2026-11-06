# -*- coding: utf-8 -*-
"""Build out_018.json from manual 記→鈔 alignment (sec17 二衣總別, z0..z149)."""
import io, os, json, sys
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')
J = json.load(io.open(os.path.join(AD, '018.json'), encoding='utf-8'))
items = J['items']
cand = J['cand']
cset = {c['c'] for c in cand}

# (z_start, z_end, c)  inclusive ranges
spec = [
    (0, 0, 0),      # 卷題/釋二衣篇、篇題總別
    (1, 2, 0),      # 敘意 夫形居世累…；順違生起；故下總分制聽；制聽名義；就下正分（初分制物、後列聽物）
    (3, 7, 3),      # 言制意者：多論/功德論/智論/十誦/雜含/華嚴/四分/多論五意/僧祇/當宗外部
    (8, 11, 4),     # 次釋名者：總名、增一、四分、慧上經、義翻三名、條數、通相縵衣
    (12, 15, 5),    # 三明功用者：大悲經、悲華五功德、僧祇禳災
    (16, 17, 7),    # 一求財如法：四邪五邪、律證、邪心辨
    (18, 21, 8),    # 二財體如：厚重熟緻、章服儀感通傳、生疎非法、僧祇龍鳥
    (22, 33, 9),    # 三色如法：上色壞色、五納、涅槃、十誦、戒本三色、多論、僧祇、蜀郡木蘭、善見、結斷
    (34, 43, 10),   # 四量是非：四分定量、業疏、度身二法、十誦僧祇婆論三品、過減、五分
    (44, 47, 11),   # 五條數多少：雙數、四分十誦、多論九品、聖跡記、智論大準
    (48, 50, 12),   # 六堤數長短：五條十隔、婆論三長一短、割截意三賤
    (51, 53, 13),   # 七重數多少：感通傳葉相、多論摘分、糞掃多重
    (54, 62, 14),   # 八作衣方法：四分僧祇中含、一端指作、五分非法、阿難條葉、緣紐鉤蘭
    (63, 65, 16),   # 三明受衣法 對首：四分缺文、古今用別、正從品數
    (66, 72, 17),   # 今先受法：先後次第、正衣從衣、縵衣、結歎、斥非法
    (73, 78, 18),   # 次明捨法：尼受二衣、祇支覆肩問答、僧祇制量
    (79, 79, 19),   # 二明心念法：獨住、捨受法
    (80, 82, 21),   # 四雜料簡 初明受捨是非：十誦五分善見多論、八指穿破、四礙
    (83, 85, 22),   # 二補治浣染：十誦却刺、母論衣和合淨、善見補治、五分四分十誦
    (86, 101, 23),  # 第三受用擎舉：十誦治禪病僧祇五分四分、了論、五百問、反著、敬護、雜含賢愚
    (102, 110, 24), # 二明作法攝衣界：自然作法、無藍須結、諸家立法、五分十誦多論、加結解法
    (111, 124, 25), # 二明坐具：制意、搩量、十誦伽論僧祇、鼻柰耶、七百結集十事、增法、多論
    (125, 125, 26), # 坐具受捨法
    (126, 127, 27), # 坐具持用：道中寺中、賢愚、漉袋制意
    (128, 132, 28), # 三漉水袋法：慈濟制意、多論僧祇四分、親行、謗者
    (133, 133, 29), # 二明聽門 分四、初門總分
    (134, 137, 31), # 百一諸長：多論百一、五分諸衣、十誦波利迦羅、善見、沙彌
    (138, 138, 34), # 僧祇支法
    (139, 142, 35), # 涅槃僧法：僧祇十誦三千五百問四分、十誦五分俱修羅
    (143, 147, 36), # 今時偏袒方裙等、十誦四分白衣外道衣、開畜僧物貴物、蚊厨帽瘡衣
    (148, 148, 37), # 邊方五事
    (149, 149, 38), # 皮革
]
z2c = {}
for a, b, c in spec:
    for z in range(a, b + 1):
        assert z not in z2c, 'dup %d' % z
        z2c[z] = c
        assert c in cset, 'c %d not in cand' % c

zs = [it['z'] for it in items]
assert len(zs) == len(set(zs)), 'dup z in items'
missing = [z for z in zs if z not in z2c]
extra = [z for z in z2c if z not in zs]
print('items', len(items), 'mapped', len(z2c), 'missing', missing, 'extra', extra)
map_ = [{'z': z, 'c': z2c[z]} for z in zs]

assert len(map_) == len(items)
bad = [(map_[i]['z'], map_[i]['c'], map_[i + 1]['z'], map_[i + 1]['c'])
       for i in range(len(map_) - 1) if map_[i]['c'] > map_[i + 1]['c']]
print('non-monotone:', bad)
from collections import Counter
cnt = Counter(m['c'] for m in map_)
print('distinct c used:', len(cnt), 'range', min(cnt), max(cnt))
print('counts:', ' '.join('c%d:%d' % (c, cnt[c]) for c in sorted(cnt)))

io.open(os.path.join(AD, 'out_018.json'), 'w', encoding='utf-8').write(
    json.dumps({'map': map_}, ensure_ascii=False, separators=(',', ':')))
print('written', len(map_))
