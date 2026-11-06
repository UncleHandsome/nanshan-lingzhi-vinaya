# -*- coding: utf-8 -*-
"""Build out_020.json — manual 記→鈔 alignment for sec18 四藥受淨 (z0..z114)."""
import io, os, json, sys
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')
J = json.load(io.open(os.path.join(AD, '020.json'), encoding='utf-8'))
items = J['items']
cand = J['cand']
cset = {c['c'] for c in cand}

# (z_start, z_end, c) inclusive
spec = [
    (0, 2, 0),      # 篇題通釋；報命支持‧釋四藥名；盡形名義‧五門分章
    (3, 14, 3),     # 時藥：四分五種蒲闍尼/佉闍尼、僧祇蔓菁、涅槃斷肉、楞伽十過、僧祇七眾、大乘學戒、四分十善、酒肉五辛
    (15, 17, 4),    # 非時漿：十四種果漿、善見木果葉華、母論破汁、了論炒米、四分八漿、伽論澄漉
    (18, 23, 5),    # 七日藥：伽論糖漿、僧祇加脂、四分五脂、僧祇百一、五分石蜜、十誦五人、僧祇穌油胡麻脂、善見鑽服、蜜
    (24, 27, 6),    # 盡形體：僧祇呵梨勒、四分不任為食、善見草木、明了論隨病為量、十誦苦酒、斥世非法
    (28, 30, 7),    # 六味定：涅槃六味、五種量、更量、大開
    (31, 31, 8),    # 轉變：中論苦酒、十誦四物轉
    (32, 32, 9),    # 相和：薩婆多從彊而服、浸豆麥
    (33, 34, 11),   # 結淨制意：上中下根、因餓死開、釋淨名四義、遮濫
    (35, 35, 13),   # 籬牆不周淨：半有多無都無、十八處
    (36, 37, 14),   # 檀越淨三種、十誦僧祇引證
    (38, 38, 15),   # 處分淨：僧祇初夜、善見竪柱三說
    (39, 46, 16),   # 白二結：五分通結、僧祇一覆別隔、白文羯磨、二同、通結問答
    (47, 49, 17),   # 加法：古師以食望僧、唱相、白二、解淨地、僧祇水流出外
    (50, 50, 18),   # 雜出料簡：治故處、停廢二年、問答
    (51, 54, 20),   # 護淨翻淨：敘益、斥非、緣淨體淨緣不淨體不淨、五分僧祇十誦善見
    (55, 62, 21),   # 問觸淨何過：六過、護淨經、智論、大集濟龍、僧護經、五百問
    (63, 69, 23),   # 護惡觸：十誦五分僧祇行食、錯捉、器中觸、舟車、擔持、佐助、鼻奈耶
    (70, 70, 24),   # 自煮：僧祇淨人病自舂、洗器自然火、煮菜薑湯溫食指教
    (71, 72, 28),   # 通塞初四藥：時藥定有宿煮、三藥加口法、十誦石蜜、四分殘宿
    (73, 74, 30),   # 四過過相：十誦三種人、四分式叉、薩婆多三種
    (75, 75, 32),   # 內宿就食：離地長足、狗持風吹
    (76, 77, 35),   # 惡觸：五種、四不成、三句分別、就食
    (78, 80, 36),   # 互覆墮：四分從根斷、五分淨不淨地、僧祇
    (81, 83, 37),   # 儉開八事：八罪、定罪、義加壞生、還制、十誦持殘
    (84, 84, 40),   # 淨生種處人：四句
    (85, 89, 41),   # 淨法：四分十種、五分十種、僧祇六物、母論二淨、十誦火淨、種相問答
    (90, 90, 43),   # 受法初門手受五義：多論五意、五分訶言
    (91, 91, 44),   # 二受通四藥：手受通四、口受局三、十誦時分藥
    (92, 92, 45),   # 三所授人：六眾三趣、薩婆多證明、善見止食三
    (93, 94, 46),   # 四受法差別：心境相當、仰手承之、除眼闇不喜驚急、預前運心
    (95, 95, 49),   # 非時藥體：八患
    (96, 96, 52),   # 非時正加口法：詞中六句
    (97, 97, 54),   # 七日藥體：改第八、犯竟殘藥
    (98, 100, 56),  # 七日所受比丘：五過、自作四法、毘婆沙
    (101, 101, 57), # 七日正加口法
    (102, 102, 61), # 盡形三所受比丘：記識、分體分
    (103, 106, 62), # 盡形四加法：丸散題名、別受、買藥、斥世
    (107, 107, 63), # 五說淨：三義、手受不須、餘三藥反前
    (108, 108, 64), # 六二受通塞：一人受已通及餘人、四分七日藥與諸比丘
    (109, 109, 65), # 七重加：五日已還更加、六日已去不得
    (110, 110, 66), # 八雜明諸相：薩婆多四段
    (111, 112, 67), # 問防護何罪：手受口受、因明生罪
    (113, 114, 68), # 問云何不生不受；盡形口生六罪
]

z2c = {}
for a, b, c in spec:
    assert c in cset, 'c %d not in cand' % c
    for z in range(a, b + 1):
        assert z not in z2c, 'dup %d' % z
        z2c[z] = c

zs = [it['z'] for it in items]
assert len(zs) == len(set(zs)), 'dup z'
missing = [z for z in zs if z not in z2c]
extra = [z for z in z2c if z not in zs]
print('items', len(items), 'mapped', len(z2c), 'missing', missing, 'extra', extra)
assert not missing and not extra

map_ = [{'z': z, 'c': z2c[z]} for z in zs]
assert len(map_) == len(items)
bad = [(map_[i]['z'], map_[i]['c'], map_[i+1]['z'], map_[i+1]['c'])
       for i in range(len(map_) - 1) if map_[i]['c'] > map_[i+1]['c']]
print('non-monotone:', bad)
from collections import Counter
cnt = Counter(m['c'] for m in map_)
print('distinct c used:', len(cnt))
print('counts:', ' '.join('c%d:%d' % (c, cnt[c]) for c in sorted(cnt)))
print('skipped:', [c for c in sorted(cset) if c not in cnt])

io.open(os.path.join(AD, 'out_020.json'), 'w', encoding='utf-8').write(
    json.dumps({'map': map_}, ensure_ascii=False, separators=(',', ':')))
print('written', len(map_))
