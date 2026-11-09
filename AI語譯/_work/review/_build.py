import csv, json, re
from collections import OrderedDict

P = "AI語譯/_work/review/report_re5.tsv"
rows = []
with open(P, encoding="utf-8") as f:
    rd = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
    header = next(rd)
    for r in rd:
        if len(r) != 10:
            continue
        rows.append(dict(zip(header, r)))

jb = [r for r in rows if r["book"] == "02_戒疏"]

def norm(s):
    return s.replace("『", "「").replace("』", "」")

def clean_b(b):
    # remove reviewer alternatives in parentheses
    b = re.sub(r"（或[^（）]*）", "", b)
    return b

MANUAL = {
 8:  [("《大乘律二十二明了論》", "《律二十二明了論》")],
 11: [("波逸提（單墮罪）", "波逸提（墮罪）")],
 24: [("但若就『保持純淨無染的根本行體』而言，第一篇自然被稱為最為尊勝。", "若就防護微細而達到純淨無染而言，則名為最為殊勝。")],
 32: [("不定與滅諍本應歸入第五篇。現在疏文說「篇聚不收攝」、「此處不加論述」，究竟是何深意尚無法詳知。", "二不定法與七滅諍法（若結犯吉羅）理應歸入第五篇；如今疏文卻說「篇聚不收攝」、「此處不加論述」，尚不清楚是何意圖。")],
 35: [("最初缺少比丘緣則是根本沒有正常的發起之處", "最初的比丘緣則非關止息")],
 36: [("依據什麼依據而陳述", "依據什麼而陳述")],
 38: [("行的行相是發作", "行的行相是起作（造作）")],
 56: [("「但同樣」以下，結合理論核心宗旨", "「但同樣」以下，總結止持宗旨")],
 57: [("全都開許不犯根本罪", "全都開許免罪")],
 58: [("有時面對並非犯罪的對象，卻誤以為是『有主之物而心生貪取』。", "有時面對非獲罪的對象，或因『將有主之物誤想為無主之物』的緣故，所以律判無罪。")],
 59: [("呈現出事相雖然統括為一、但所獲罪名卻各自有別的局面。", "呈現出事相心態統括為一、而罪相心態各自有別的局面。")],
 60: [("「所獲罪名各自有別」", "「罪相有別」")],
 65: [("「若能」以下分別顯露", "「順」以下分別顯露"), ("「若是」以下，展示犯戒的相貌", "「愚」以下，展示犯戒的相貌")],
 66: [("「法規」以下，確立理論基礎", "「法」以下，確立理論基礎"), ("「這與」以下，斥責破除古德的舊說", "「不同」以下，斥責破除古德的舊說")],
 77: [("口業也是如此，必須仰賴他人的身業等助成，絕無單獨一種業就能成辦殺盜之理", "身造口業也是如此，亦須仰賴他人（施主言語）的口業助成，絕無單獨一種業就能成辦之理")],
 78: [("對方只是依著施主之言而信", "受騙的施主只是依著自己所立之言而信以為真")],
 79: [("自認「我是聖人」而起坐穿衣，必定藉助他人的言說領會，即是口業相助", "如施主言「若是聖人應當起立」而凡夫起立，必定藉助他人所說之話，這即是口業相助")],
 96: [("特定的特定心（剋心）", "特定的加害心（剋心）")],
 106: [("這當中只要所涉及的衣服價值滿五錢者", "這當中只要應分給同夥的半份衣物價值滿五錢者")],
 119: [("預先派遣劊子手去殺戮某人，送信的人遲緩尚未抵達", "預先派遣使者去殺戮某人，使者走得遲緩尚未抵達"), ("信差剛好到達並立即將人殺死", "使者剛好到達並立即將人殺死")],
 124: [("「這標示」以下", "疏文自「此」字以下")],
 138: [("戒本文字省略了其餘細節果報", "疏文省略了其餘果報")],
 139: [("第四、廣教文相所詮釋的持犯核心，不超出開許、遮止、違犯、不犯這「四種行相」；", "第四、廣教文相所詮釋的內容，不超出四種行相（即犯、不犯、輕、重）；")],
 140: [("不超出僧伽修證的「六種位階」", "不超出六種範疇（即深防、限分、約相、示過、心境、內外）")],
 153: [("是指深信三藏中所說的各種修行法門", "是指三藏中所說的各項行持")],
 154: [("裁結罪名的名稱", "裁結罪名")],
 155: [("是順應著違犯者而隨機補訂結罪的", "是各隨一人犯過而隨後制結（一人隨結）")],
 156: [("都受這套持犯規律所規範", "都要受持這部犯法（戒本）")],
 159: [("，總結文意", "")],
 169: [("是指引《律藏》文句做廣泛解釋", "是指明《律藏》中的「廣解」")],
 170: [("前半段說明被仇敵強行按抓著、推向受害者身上", "前半段說明被仇敵強行捉住、帶往行淫對象（前境）處")],
 171: [("是指引導特定的人物，依照戒律所規定的罪名來判定科罰", "是援引其人（比丘）、依照戒法科斷（波羅夷）")],
 172: [("「引導人物」就是指這名比丘", "「援引其人」就是指比丘")],
 173: [("如果作了出罪羯磨法之後", "如果作了（與波羅夷治罰羯磨）法之後")],
 185: [("從「然而我所」往下，指出廣泛著作引發學習", "從「然而我所」往下，是指示廣本（《事鈔》已具）以生起此處之略解")],
 199: [("第十三、「私度關塞偷稅」", "第十三、「私度關塞」")],
 207: [("隨即解除約定，犯突吉羅罪。", "隨即解除約定，犯突吉羅罪。」")],
 226: [("無論動機是為自己還是為他人，只要對方死亡，相關教唆者全都結犯根本重罪。", "不論是指使者自己還是受指使的他人，只要對方死亡，兩者全都結犯根本重罪。")],
 228: [("經文之所以不再提及「第七個七天」", "疏文之所以不提及「第七個七天」")],
 230: [("經文從「拿刀」以下", "律文從「拿刀」以下")],
 236: [("因此在重大罪愆中列於首位", "因此既列名於四重禁戒（四夷之末），又居於四語業之首")],
 237: [("其功德尊貴，故冒稱者同獲重罪。", "")],
 238: [("在第一門「時機」中", "在第一門辨「時代時期」中")],
 239: [("依據偷盜的原產地來判定", "依據偷盜的原本處所來判定")],
 240: [("在第四句律文中，標明科意，點明文義，淺顯易解。", "在解釋第四句的初科「標」之中，疏文僅點出律文，文義已清楚可解。")],
 246: [("《善見》五事的文字中略去了「隨身受用物」一項。", "疏文中略去了「隨身受用物」一項。")],
 259: [("是指稱念出入之氣息，從一數到十", "是指計算出入之氣息，從一數到十")],
 260: [("第五句從「是比丘」往下，將犯人與罪名相結合，列入僧團處罰擯除的規定相狀。", "第五句從「是比丘」往下，是將犯人與罪名相結合；第六句是列入僧團處罰擯除的規定相狀。")],
 261: [("或者差遣者發狂發癲、捨戒退位等，教唆者不結根本重罪", "或者能教與所使任一方發狂發癲、捨戒退位等，教唆者不結根本重罪")],
 262: [("不知戒律法度的僧人，見狀便合掌稱頌叫好，或者攙扶接引他們攀登險峰，或者替他們準備繩索工具。這就是教唆與讚歎，完全符合違犯殺戒的罪狀，「身口二業同時顯露」，指的就是這一類事情。", "不知戒律法度的人，合掌稱揚讚歎，或者攙扶接引他們攀登高山，或者替他們準備繩索工具。這就是教唆與讚歎，完全符合違犯殺戒的罪狀，注文所說的「身口同時顯露殺相」，指的就是這一類事情。")],
 265: [("其次辨析解釋名稱，包含輕重、分合這三層意涵。", "其次辨析釋名、輕重、離合這三種意旨。")],
 266: [("由內心或外在境緣生起的心態不同", "起心期於體內交會（內觸）或體外摩觸（外觸）不同")],
 277: [("或者有人問：「你入定境了嗎？」比丘回答：「我今天不入世間禪定。」對方又問：「昨天如何？」", "或者比丘自稱：「我今天不入世間禪定。」對方問道：「昨天如何？」")],
 305: [("第二句之下，省略了「摶收覆蔽」的字眼。第三句之上，省略了「未取衣服」的字眼。", "第二句之下，省略了「摶覆（以磚石覆蓋）」二字。第三句之上，省略了「不取」二字。")],
 310: [("將貴重物判歸為輕物即結不可悔重罪（波羅夷），將輕物判歸貴重物則結粗惡罪（偷蘭遮）", "將常住重物判入現前輕物即結不可悔重罪（波羅夷），將現前輕物判歸常住重物則結粗惡罪（偷蘭遮）")],
 311: [("「劃完一頭結輕罪」", "「寫完一端結輕罪」"), ("「劃完兩頭結重罪」", "「兩端俱寫完結重罪」")],
 312: [("順應不犯的法則便能成就", "順從不犯之法而成就犯戒")],
 313: [("是告誡大眾的心思", "是向大眾宣告情事")],
 314: [("同樣都屬於破壞僧團的一類", "同樣破壞僧團的和合一體")],
 315: [("斷頭是依據喪失戒體果報來做比喻，重複犯戒是依據比丘戒律的名分依然存在來說的", "斷頭是依據喪失比丘資格的結果來做比喻，重複犯戒是依據其餘戒體依然存在來說的")],
 336: [("戒羸不自悔", "戒力羸弱而不自悔（不陳白捨戒）")],
}

SKIP = {
 12: "已套用（不妨礙已補）",
 47: "無 suggestion",
 48: "無 suggestion",
 49: "無 suggestion",
 179: "已套用（擴充語已存在）",
 188: "已套用（引號已為」）",
 202: "已套用（末二句已譯）",
 215: "無 suggestion",
 216: "無 suggestion",
 247: "無 suggestion",
}

POST = [
    ("，要求其徹底斷除殺生，要求其徹底斷除殺生。」", "，要求其徹底斷除殺生。」"),
    ("自己的衣服（白衣/自衣）", "自己的衣服"),
    ("只因為既然有明確教法依循", "只因為既有明確教法依循"),
]

segs = OrderedDict()
for i, r in enumerate(jb):
    segs.setdefault((r["chunk"], r["seg"]), r["current"])
base_of = dict(segs)

log = []
applied_rows = 0
skipped_rows = 0
errors = []

for i, r in enumerate(jb):
    key = (r["chunk"], r["seg"])
    t = segs[key]
    if i in SKIP:
        skipped_rows += 1
        log.append((i, key, "SKIP", SKIP[i]))
        continue
    if r["suggestion"].strip() == "":
        skipped_rows += 1
        log.append((i, key, "SKIP", "無 suggestion"))
        continue
    if i in MANUAL:
        ok = True
        for old, new in MANUAL[i]:
            c = t.count(old)
            if c != 1:
                errors.append((i, key, "MANUAL count=%d" % c, old[:40]))
                ok = False
                continue
            t = t.replace(old, new, 1)
        if ok:
            segs[key] = t
            applied_rows += 1
            log.append((i, key, "MANUAL", "%d edits" % len(MANUAL[i])))
        continue
    # mechanical
    pairs = re.findall(r"「([^」]{1,200})」\s*(?:改為|改成|改譯為|修訂為|應改為)\s*「([^」]{1,400})」", r["suggestion"].strip())
    if not pairs:
        errors.append((i, key, "NOPAIR", r["suggestion"][:40]))
        continue
    ok = True
    for a, b in pairs:
        b = clean_b(b)
        if a in t:
            if t.count(a) != 1:
                errors.append((i, key, "MECH count=%d" % t.count(a), a[:30]))
                ok = False
                continue
            t = t.replace(a, b, 1)
        elif norm(a) in t:
            na, nb = norm(a), norm(b)
            if t.count(na) != 1:
                errors.append((i, key, "MECHN count=%d" % t.count(na), a[:30]))
                ok = False
                continue
            t = t.replace(na, nb, 1)
        else:
            errors.append((i, key, "MECH nofind", a[:40]))
            ok = False
    if ok:
        segs[key] = t
        applied_rows += 1
        log.append((i, key, "MECH", "%d pairs" % len(pairs)))

print("applied", applied_rows, "skipped", skipped_rows, "errors", len(errors))
for e in errors:
    print("ERR", e)

# post-pass polish
post_hits = 0
for old, new in POST:
    found = 0
    for key in segs:
        if old in segs[key]:
            found = segs[key].count(old)
            segs[key] = segs[key].replace(old, new)
            post_hits += found
    print("POST", old[:12], "hits", found)

# output
out = "AI語譯/_work/review/fix_re5_g1.tsv"
bad = []
written = 0
chunk_order = {}
for (chunk, seg) in segs:
    chunk_order.setdefault(chunk, len(chunk_order))
def sort_key(item):
    chunk, seg = item[0]
    try:
        sn = int(seg)
    except ValueError:
        sn = 10 ** 9
    return (chunk_order[chunk], sn, seg)
with open(out, "w", encoding="utf-8", newline="\n") as f:
    for (chunk, seg), t in sorted(segs.items(), key=sort_key):
        if t == base_of[(chunk, seg)]:
            continue
        if "\t" in t or "\n" in t or "\r" in t:
            bad.append((chunk, seg))
        f.write("02_戒疏\t%s\t%s\t%s\n" % (chunk, seg, t))
        written += 1

print("out segs", len(segs), "written", written, "bad", bad)
print("len out", sum(len(t) for t in segs.values()))
import io
print("maxlen", max(len(t) for t in segs.values()))
