# -*- coding: utf-8 -*-
"""Build out_021.json: 記段(z0..z41) → 鈔段(c0..c29) for sec19 鉢器制聽."""
import io, os, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'

# z -> c  (c non-decreasing; c only from cand 0..29)
MAP = {
    0: 0,    # 篇題/釋題開始（含前篇藥文尾）
    1: 0,    # 釋鉢器篇題：鉢/器/制聽二教
    2: 0,    # 敘意：養生眾具、二教通收
    3: 0,    # 敘意：隨報/事資道立/違則斯制/分條格
    4: 3,    # 制門 制意（僧祇/十誦/善見）
    5: 4,    # 二體：五分十誦簡非法、佛作鉢坯
    6: 4,    # 二體：業疏、五分偷蘭、僧祇外道標、總判
    7: 4,    # 體第三科（麥紵/棍瓦/瓷鉢）+ 色初科起
    8: 5,    # 三色：鴿色、熏鉢鑪法、斥非
    9: 5,    # 三色：熏磨/油塗/親聞/善見/諸部/此方
    10: 6,   # 四量：三品、周斗、孫子算經
    11: 6,   # 四量：唐斗、十誦鉢他
    12: 6,   # 四量：鉢他、僧祇四升、婆論
    13: 6,   # 四量：鉢他量、釜飯、合鉢量
    14: 6,   # 四量：律師異議、母論、定教量、斥非法
    15: 6,   # 四量末斥執小鉢 + 加受法起
    16: 7,   # 五加受法：常用、善見心念、僧祇十日
    17: 8,   # 六失受：主言不言、買鉢、孔罅、三衣例
    18: 9,   # 七行護：五百問開離、五分歠粥、母論洗鉢
    19: 9,   # 行護：先師後己、串、洗衣、破鉢、十誦
    20: 9,   # 行護：五分護法、四分十三安處、僧祇六事
    21: 9,   # 行護：萬字、補治、安處、洗法、帶持
    22: 9,   # 行護：口外向、掛鉢、肩上；聽門總標起
    23: 11,  # 聽門：十六杖器、鐵作具、熏鉢物、作衣具
    24: 11,  # 聽門：火具、諸鉢、龍牙杙、簡非
    25: 12,  # 鍵𨨲註 + 二 步挽車
    26: 13,  # 車末簡非 + 三 鍼/帶 + 四 屐 + 五 拂起
    27: 15,  # 五 拂：僧祇線拂、五百問麈尾、四分尾拂
    28: 17,  # 尾拂毛 + 六 長床 + 七 文相交雜（十段）
    29: 17,  # 七 文相交雜：染草、藥具、食具、澡洗、斗秤
    30: 18,  # 七末五分 + 八 供給和上（五段）
    31: 19,  # 八末刀鑷 + 九 供給住房（八段）
    32: 19,  # 九 供給住房：錫杖、扇、作食具
    33: 19,  # 九末食具/浴室/香嚴 + 十 浴室（四段）
    34: 20,  # 十 浴室：母論說法 + 十一/十二 起
    35: 22,  # 十二 坐禪法：禪毱/禪鎮/骨人/好師
    36: 22,  # 坐禪末好照/衣服 + 十三/十四/十五 短科
    37: 26,  # 十六 房舍：招提、作房、修治
    38: 27,  # 十七 佛自執作、僧坊、上座、迦葉、多論
    39: 28,  # 十七末 + 十八 僧祇畫壁、四分嚴飾、別房、僧地
    40: 28,  # 十八 九十日、治故房、五分題名、十誦互施
    41: 28,  # 十八 奪一與一、賞功、僧祇破房
}

Z = {}
s = io.open(os.path.join(D, '_a021_ji.txt'), encoding='utf-8').read()
for m in re.finditer(r'\[z(\d+)\] (.*?)(?=\n\n|\Z)', s, re.S):
    Z[int(m.group(1))] = m.group(2).strip()

J = json.load(io.open(os.path.join(D, '021.json'), encoding='utf-8'))
zs = [it['z'] for it in J['items']]
assert zs == list(range(len(zs))), zs
assert set(zs) == set(MAP), (set(zs) ^ set(MAP))
cset = {cd['c'] for cd in J['cand']}
prev = -1
for z in zs:
    c = MAP[z]
    assert c in cset, (z, c)
    assert c >= prev, ('non-monotone', z, c, prev)
    prev = c
out = {'map': [{'z': z, 'c': MAP[z]} for z in zs]}
io.open(os.path.join(D, 'out_021.json'), 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print('written', len(out['map']), 'items')
for z in zs:
    print('z%-2d c%-2d %s' % (z, MAP[z], Z[z][:34]))
