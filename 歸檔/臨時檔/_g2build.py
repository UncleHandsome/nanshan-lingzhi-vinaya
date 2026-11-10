# -*- coding: utf-8 -*-
import sys, json, io, os, re
sys.stdout.reconfigure(encoding="utf-8")

BASE = r'AI語譯\out\04_比丘尼鈔'
rows = json.load(open('_g2rows.json', encoding='utf-8'))

_cache = {}
def blocks(ch):
    if ch not in _cache:
        txt = io.open(os.path.join(BASE, ch + '.txt'), encoding='utf-8').read().replace('\r\n', '\n')
        _cache[ch] = [b.strip() for b in txt.split('\n\n') if b.strip()]
    return _cache[ch]

def clean(s):
    return s.replace('\r', '').replace('\n', '').replace('\t', '').strip()

def base_text(ch, seg):
    return clean(blocks(ch)[int(seg) - 1])

# rows already applied / superseded / superfluous
SKIP = {15, 63, 101, 113, 132, 153, 165, 173,   # B already in live
        30, 40, 45, 46, 92, 94, 96, 99, 100,     # same fix as sibling row / superseded
        69,                                       # seg84 closing quote of continuous quotation
        29, 70, 47}                               # already covered by MAN below

ops = {}   # (chunk, seg) -> list of [old, new, src]

def add(ch, seg, old, new, src):
    ops.setdefault((ch, seg), []).append([old, new, src])

# ---- auto pairs (verbatim A -> B) ----
auto = [x for x in json.load(open('_g2auto.json', encoding='utf-8')) if x[3] == 'APPLY']
auto2 = json.load(open('_g2auto2.json', encoding='utf-8'))
Bfix = {
    86: '《摩得勒伽論》也問',
    122: '第二是結夏時間',
    131: '求請依止者必須具備五種心法',
    166: '一是不受食戒',
    39: '求戒弟子雖然知道和尚犯了重罪，但不知道向這樣的人受戒是不得戒的，佛律也開許其受戒成就',
    93: '例如酥、油、生酥、蜜、石蜜（冰糖）等滋補藥品',
}

# ---- manual ops ----
MAN = [
 # 01b seg5 row47  (trimmed: the clause "，法事也能成立" already follows in the base)
 ('01b_卷上之上', '5',
  '如果是為了救濟那些正在接受處罰的僧人，羯磨時特許站立',
  '若是慈濟或處治之法，特許站立', 47),
 # 01a seg35  (row 29 == row 30)
 ('01a_卷上之上', '35',
  '如果內部沒有戒場，就可以從內側唱大界內相；如果東北兩邊建有矮牆，應當順著矮牆東南角的外側起唱',
  '如果沒有戒場，就可以從牆內側唱界（外相）。宣唱大界內相時，東北兩邊若建有矮牆，應當順著矮牆東南角的外側起唱', 29),
 # 01b seg85 row70
 ('01b_卷上之上', '85',
  '第二、式叉摩那被判定不淨的食物，大尼如果為其作了淨法便可以食用，但若大尼判定為不淨的食物，式叉摩那也絕對不能吃；',
  '第二、式叉摩那的不淨食（如犯宿觸等），大比丘尼食用仍算清淨；而大比丘尼的不淨食，式叉摩那食用也同樣是不淨；', 70),
 # 01b seg85 row71
 ('01b_卷上之上', '85',
  '第七、式叉尼布薩日（隨僧說戒）；',
  '第七、式叉尼布薩日（半月入僧中自白清淨）；', 71),
 # 01b seg94 row74
 ('01b_卷上之上', '94',
  '僧團正式作法時，問和答云：「僧團現今和合，所為何事？」回答：「作給予畜收徒眾資格的羯磨。」',
  '僧團正式作法時，問：「僧團現今和合，所為何事？」答云：「作給予畜收徒眾資格的羯磨。」', 74),
 # 02a seg52 row90
 ('02a_卷上之下', '52',
  '這時她才回頭說：「我早就知道有這件事了。」此人就不再是比丘尼',
  '這時知情者才回頭說：「我早就知道有這件事了。」那麼這位知情隱瞞者就不再是比丘尼', 90),
 # 02b seg1 row105
 ('02b_卷上之下', '1',
  '《僧祇律》又說：不可同時點連在一起，或點一、三、五、七、九處等，也不可畫成花朵的形狀；',
  '《僧祇律》又說：不可將點連成一片；點的數量可以是一、三、五、七、九點等（取奇數），但不可排列成花朵的形狀；', 105),
 # 02b seg107 row118
 ('02b_卷上之下', '107',
  '如果說戒師尚未誦完戒序、正在唱問「大眾在戒法之中是否清淨」之時',
  '如果客尼在說戒師尚未誦戒序唱問「大眾在此中是否清淨」之前來到', 118),
 # 02b seg120 row121
 ('02b_卷上之下', '120',
  '僧眾意見難以和諧統一',
  '僧眾平日難以召集齊全（僧眾難以和集）', 121),
 # 03a seg5 row123
 ('03a_卷中之上', '5',
  '第二門「結界時間」：',
  '第二門「結夏時間」：', 123),
 # 03b seg3 row133 (whole block)
 ('03b_卷中之上', '3',
  '本篇大門共有十一項：第一敬寺、第二敬佛、第三敬法、第四敬僧、第五定尊、第六致拜、第七八敬、第八報恩、第九醫藥、第十殯終（原文標題作十一項，實列十項，疑為古抄脫漏或併項所致）。',
  '本篇大門共有十項：第一敬寺、第二敬佛、第三敬法、第四敬僧、第五定尊、第六致拜、第七八敬、第八報恩、第九醫藥、第十殯終。', 133),
 # 03b seg4 row134
 ('03b_卷中之上', '4',
  '《五百問事》中記載：古時有一位面相師為婆羅門看相，見到一位比丘具有天子之相；',
  '《五百問事》中記載：古時有一位懂相術的婆羅門，為一位比丘看相，見其具有天子之相；', 134),
 # 03b seg6 row136
 ('03b_卷中之上', '6',
  '以致「三豕涉河」般的傳寫錯亂、孔子辨「獻鼠」為獻璞之疑；使玉石般的妙經失去感應的功效',
  '以致如西河傳書之訛亂了孔子之道，如周人獻死鼠而疑為未琢之玉璞；使得經典失去感應的功效', 136),
 # 03b seg23 row148 (whole block)
 ('03b_卷中之上', '23',
  '第六、佛像與埋藏珍寶互換（像共寶互）：是指住持三寶所用的佛像等器物，與埋藏以備荒年的僧寶資財互相私自挪用，同樣結犯罪過。',
  '第六、住持三寶物與理體三寶物互換（像共寶互）：是指住持三寶之物與理體三寶（理寶，原文訛作埋寶）之物互相私自挪用，同樣結犯罪過。', 148),
 # 03b seg24 row149
 ('03b_卷中之上', '24',
  '更換下來的舊柱子轉施給僧眾，僧眾也不得擅自挪為私用',
  '更換下來的舊柱子轉施給僧眾，僧眾也不得受用', 149),
 # 03b seg26 row150
 ('03b_卷中之上', '26',
  '若是用殘破劣器盛盛給他',
  '若是用殘破劣器盛食給他', 150),
 # 03b seg27 row151
 ('03b_卷中之上', '27',
  '如果官府不答應沒收，則如數歸還',
  '如果官府不准許帶走，則交還官府', 151),
 # 04a seg10 row156
 ('04a_卷中之下', '10',
  '因此律中說：若干種界的四相包括：一周圍有完整圍牆',
  '因此律中說『若干界』。四相為：一周圍有完整圍牆', 156),
 # 04a seg23 row161
 ('04a_卷中之下', '23',
  '隨著男子一個個起身又躺下，一一各得十個波逸提罪；隨著男子每一次轉身，也各得十個波逸提罪',
  '（比丘尼）隨每一次起身又躺下，每一次各得十個波逸提罪；隨每一次翻身轉側，也各得十個波逸提罪', 161),
 # 04a seg30 row164
 ('04a_卷中之下', '30',
  '若白衣人家向僧團借用僧臥具，用齋完畢不予收起，也犯波逸提罪',
  '若在白衣家借用僧團臥具，（比丘尼）用齋完畢不予收疊，也犯波逸提罪', 164),
]

for x in MAN:
    add(x[0], x[1], x[2], x[3], x[4])

# auto + auto2
for i, ch, seg, st, A, B in auto:
    if i in SKIP: continue
    add(ch, seg, A, Bfix.get(i, B), i)
for i, ch, seg, A, B in auto2:
    if i in SKIP: continue
    add(ch, seg, A, Bfix.get(i, B), i)

# 01b seg79-83: strip trailing closing quote (report rows 64-68)
STRIPQ = {'79': 64, '80': 65, '81': 66, '82': 67, '83': 68}
for seg in sorted(STRIPQ):
    t = base_text('01b_卷上之上', seg)
    assert t.endswith('」'), (seg, t[-5:])
    add('01b_卷上之上', seg, '@@ENDQUOTE@@', '', STRIPQ[seg])

# ---- apply ----
order = {'01a_卷上之上': 0, '01b_卷上之上': 1, '02a_卷上之下': 2, '02b_卷上之下': 3,
         '03a_卷中之上': 4, '03b_卷中之上': 5, '04a_卷中之下': 6, '04b_卷中之下': 7}
outlines = []
problems = []
used_rows = set()
for key in sorted(ops, key=lambda k: (order[k[0]], int(k[1]))):
    ch, seg = key
    t = base_text(ch, seg)
    for old, new, src in ops[key]:
        if old == '@@ENDQUOTE@@':
            if not t.endswith('」'):
                problems.append((ch, seg, src, 0, 'NO-END-QUOTE'))
                continue
            t = t[:-1]
            used_rows.add(src)
            continue
        n = t.count(old)
        if n != 1:
            problems.append((ch, seg, src, n, old[:60]))
            continue
        t = t.replace(old, new, 1)
        if isinstance(src, int):
            used_rows.add(src)
    if '\n' in t or '\t' in t:
        problems.append((ch, seg, 'NEWLINE', 0, ''))
    outlines.append((ch, seg, t))

print('segments out:', len(outlines), 'problem ops:', len(problems))
for p in problems:
    print('  PROBLEM', p)
json.dump(outlines, open('_g2out.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(sorted(used_rows), open('_g2used.json', 'w', encoding='utf-8'))
print('used rows', len(used_rows))
