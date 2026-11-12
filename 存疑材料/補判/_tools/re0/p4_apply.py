# -*- coding: utf-8 -*-
"""Part 1: apply the 4 是錯 items belonging to 01_行事鈔; build 待套用_re0.tsv for 03_業疏."""
import os, re, sys, shutil, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUTJ = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "re0修正前")
SU = os.path.join(ROOT, "存疑材料")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

def chunkfile(book, pfx):
    d = os.path.join(OUTJ, book)
    return os.path.join(d, sorted(f for f in os.listdir(d) if f.startswith(pfx) and f.endswith(".txt"))[0])

def blockpos(lines, seg):
    """return (start,end) line indexes of the non-empty paragraph #seg"""
    idx = [i for i, l in enumerate(lines) if l.strip()]
    i = idx[seg - 1]
    return i

# ---------------- 4 edits (01_行事鈔) ----------------
EDITS = [
    ("01_行事鈔", "01a", 63,
     "（謂其人仍足僧數，擯羯磨得成，待考）；", "（謂其人仍足僧數，擯羯磨得成）；",
     "re0 01a_卷上之一#63", "刪去「待考」存疑按語（本案判斷：正文雜入譯者存疑按語）"),
    ("01_行事鈔", "01a", 63,
     "樹上比丘——原文總稱「十二種人」〔註：此處所列僅十種，加前睡眠亦僅十一，疑有脫略；待查《十誦律》原文及《資持記》，待考〕。",
     "樹上比丘，總為十二種人。",
     "re0 01a_卷上之一#63", "依建議刪去計數存疑註，正譯為「總為十二種人」"),
    ("01_行事鈔", "01a", 68,
     "其相狀如「室宿」中所說〔註：出處待考〕。", "其相狀如「與女人同室宿戒」中所說。",
     "re0 01a_卷上之一#68", "依建議落實名相，作「與女人同室宿戒」，並刪去出處待考註"),
    ("01_行事鈔", "01b", 50,
     "二是違背其心意的治罰，以及當事人無心領納的人，就沒有乞辭，此時應作舉罪、憶念、證正、知法〔按：此四者或係治罰前之方便次第，或係四種羯磨名，待《資持記》覆核〕〔按：「知法」及「無心領」之確解待考，暫不補義〕。",
     "二是違背其心意的治罰，以及無心識領受處罰者，就沒有乞辭，此時應作舉罪、令其憶念、審驗屬實、令知罪法。",
     "re0 01a_卷上之一#50（實際段落為 01b#50）", "依建議刪去兩處按語，正譯「作舉、憶念、證正、知法」為四步驟，並補譯「知法」"),
    ("01_行事鈔", "01b", 61,
     "也必須人、事兩方面都真實具足〔按：「兩具」確解待考，暫存原文〕。",
     "也必須兩項條件（離衣須身病與衣重，乞杖須年老與患病）皆真實具足。",
     "re0 01b_卷上之一#59（實際段落為 01b#61）", "依建議正譯「兩具」為離衣（身病＋衣重）、乞杖（年老＋患病）兩項條件"),
]

# group edits by file
byfile = {}
for book, pfx, seg, old, new, src, why in EDITS:
    byfile.setdefault((book, pfx), []).append((seg, old, new, src, why))

log = []
tsv_rows = []
for (book, pfx), edits in byfile.items():
    p = chunkfile(book, pfx)
    raw = rd(p)
    lines = raw.split("\n")
    n_before = sum(1 for l in lines if l.strip())
    # backup
    bdir = os.path.join(BAK, book)
    os.makedirs(bdir, exist_ok=True)
    bp = os.path.join(bdir, os.path.basename(p))
    if not os.path.exists(bp):
        shutil.copy2(p, bp)
    for seg, old, new, src, why in edits:
        li = blockpos(lines, seg)
        cand = [i for i in range(len(lines)) if old in lines[i]]
        if len(cand) != 1:
            log.append(f"SKIP {book}/{pfx}#{seg} :: old fragment count={len(cand)}")
            continue
        i = cand[0]
        if i != li:
            log.append(f"WARN {book}/{pfx}#{seg} :: fragment on line {i}, paragraph line {li}")
        lines[i] = lines[i].replace(old, new, 1)
        log.append(f"OK   {book}/{pfx}#{seg} :: {src} :: {why}")
    out = "\n".join(lines)
    n_after = sum(1 for l in out.split("\n") if l.strip())
    if n_after != n_before:
        log.append(f"ERROR paragraph count changed {n_before}->{n_after} in {p}")
    wr(p, out)

# ---------------- deferred 11 (03_業疏) ----------------
DEFER = [
    ("1577-0006", "03_業疏", "02a", 30,
     "只要全都具備身口意三根清淨、沒有非法的相狀", "只要全都具備見、聞、疑三根清淨、沒有非法的相貌",
     "「三根」誤作身口意三根；律典「三根」專指見、聞、疑三根清淨（《業疏》卷一後文自釋「故律取三根清淨」）"),
    ("1581-0013", "03_業疏", "02a", 85,
     "以七種羯磨治罰違紀之人、諫責作證等法，這是指秉持白四羯磨",
     "以七種治罰法治人，以及規諫、證正等法，是指秉行白四羯磨",
     "「諫責作證」模糊白四羯磨名相：「諫」指諫破僧等白四諫法，「證」指憶念、不癡、罪處所等滅諍證正"),
    ("1584-0013", "03_業疏", "02b", 23,
     "作白召喚（受者）、和尚入眾自然是為了成辦事務",
     "作白召喚受者入眾，這自然是為了解決事緣",
     "受戒法中和尚安坐僧中，無「和尚入眾」之儀；「白召和入」指作白召受者、和僧令其入眾"),
    ("1584-0017", "03_業疏", "02b", 27,
     "羯磨之法是為救濟時宜，通稱為和白，",
     "並非可以用「羯磨法是為通濟時宜，通通稱為和合白法」來說明。",
     "漏譯關鍵否定詞「非」，將疏主破斥之辭誤作立論，義理顛倒"),
    ("1585-0021", "03_業疏", "02b", 48,
     "就是指在下文〈具緣〉第四之中詳細闡明諸界的體相。",
     "就是指在下文作法具緣第四門之中，詳細闡明各種結界的體相。",
     "《隨機羯磨》十篇中無〈具緣篇〉；「具緣第四」是〈集法緣成篇〉下具緣十門之第四門（約界明集）"),
    ("1587-0020／0021", "03_業疏", "02b", 88,
     "是對著現前的懺主（受懺者）作證明，因為此罪通於三種悔法的緣故。",
     "是對著現前的懺主（受懺者）作證明，這是因為墮罪通於僧中、多人、一人三處懺悔的緣故。",
     "「罪通三悔」為三十捨墮專用術語，指財通三捨、罪通三悔（僧中、多人、一人），非泛稱三種悔法"),
    ("1587-0020／0021", "03_業疏", "02b", 89,
     "罪過通於三品懺悔，前面文中已經說明。", "墮罪通於僧中、多人、一人三處懺悔，前面文中已經說明。",
     "同上一條：記文「罪通三悔」應譯出三處懺悔之法相"),
    ("1587-0029", "03_業疏", "02b", 97,
     "三人以下通途推行五種因緣", "三人以下，通用這五種法事之緣",
     "「五緣」承接上文「約文五法」（捨懺、說、恣等五事），非哲學意義之五種因緣"),
    ("1589-0006", "03_業疏", "02b", 124,
     "大界中不行三小界的各種解界法，其餘則都通用。",
     "大界中不行三小界法及各種解界法，其餘法事則都通融可行。",
     "應斷讀為「大界不行『三小』、『諸解』」：大界中既不行三小界法，亦不行諸解界法；今譯合為一事，遺漏甚大"),
    ("1591-0012", "03_業疏", "03a", 15,
     "就是前面總論義理分判廣略時所說的", "就是指前面「總義分」的「廣釋」科中所說的",
     "「總義分」是上位科名、「廣」是子科名，非「總論義理分判廣略」"),
    ("1592-0006", "03_業疏", "03a", 22,
     "例如非時的二種和合、因諍事的四種增長、觸惱僧、論法、言說餘語等即是。",
     "例如非時的二種和合白、因諍事而立的四種增日白、觸惱白、論法白、餘語白等便是。",
     "「增」即增日（推延日期），「四增日白」是單白三十九法之四種因諍延後說戒自恣之法；今譯誤刪「日」字並作「四種增長」"),
    ("1595-0021", "03_業疏", "03a", 89,
     "第五、二十七還衣之法", "第五、二十七種捨墮還衣法",
     "「二十七」指除金銀錢寶貿易三戒外其餘二十七條捨墮之還衣法，非戒條序號"),
]

def get_para(book, pfx, seg):
    p = chunkfile(book, pfx)
    lines = rd(p).split("\n")
    idx = [i for i, l in enumerate(lines) if l.strip()]
    return p, lines, idx[seg - 1]

fixed = 0
for gid, book, pfx, seg, old, new, why in DEFER:
    p, lines, li = get_para(book, pfx, seg)
    cur = lines[li]
    if old not in cur:
        log.append(f"DEFER-MISS {gid} {book}/{pfx}#{seg} :: fragment not found (可能已被他人修改)")
        tsv_rows.append([gid, book, pfx, str(seg), "", "原句已不存在（已被他人修改），未列入新段落：" + why])
        continue
    if cur.count(old) != 1:
        log.append(f"DEFER-DUP {gid} {book}/{pfx}#{seg} :: count={cur.count(old)}")
    newpara = cur.replace(old, new, 1)
    tsv_rows.append([gid, book, pfx, str(seg), newpara, why])
    fixed += 1

# write tsv
tsv = os.path.join(SU, "待套用_re0.tsv")
with open(tsv, "w", encoding="utf-8", newline="\n") as f:
    f.write("段號\t書\tchunk\t段序\t新段落\t理由\n")
    for r in tsv_rows:
        if not r[4]:
            continue
        f.write("\t".join(r) + "\n")

with open(os.path.join(SU, "補判", "_tools", "apply.log"), "w", encoding="utf-8") as f:
    f.write("\n".join(log) + f"\n\ndeferred rows with new para: {fixed}\n")
print("edits done; deferred rows:", fixed)
