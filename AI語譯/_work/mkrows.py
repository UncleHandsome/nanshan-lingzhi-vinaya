# -*- coding: utf-8 -*-
import os, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
sys.path.insert(0, r"AI語譯\_work")
from edits import EDITS

w = json.load(open(r"AI語譯\_work\work2.json", encoding="utf-8"))
# 以 (base, src) 建索引；每 base 可能有 2 條（044-0001 return/re2、259-0001 (1)/(2)、459-0009 兩條）
rows = sorted(w, key=lambda r: (r["book"], r["chunk"], r["found"], r["base"], r["src"]))

APPLIED = {
 "044-0001":"re2.txt", "053-0001":"re2.txt", "057-0003":"re2.txt", "059-0001":"re2.txt",
 "064-0001":"re2.txt", "066-0003":"re2.txt", "069-0001":"re2.txt",
 "05a_卷中之一-10":"re2.txt", "05a_卷中之一-11":"re2.txt", "080-0001":"re2.txt",
 "111-0001":"re2.txt", "09a_卷下之一-04":"re2.txt", "196-0001":"re2.txt",
 "205-0002":"re2.txt", "210-0001":"re2.txt", "212-0002":"re2.txt", "217-0002":"re2.txt",
 "224-0001":"re2.txt", "231-0005":"re2.txt", "240-0003":"re2.txt", "241-0006":"re2.txt",
 "432-0001":"return.txt", "455-0011":"re2.txt", "459-0004":"re2.txt",
 "459-0009":"*", "476-0012":"re2.txt", "484-0002":"re2.txt", "486-0002":"re2.txt",
 "560-0013":"return.txt", "208-0001":"re2.txt",
}
SKIPNOTE = {
 ("044-0001","return.txt"): "判斷所指「擅補（《薩婆多論》）」已由前批刪除，本條建議＝當時原譯；本批改由 re2 條修「緣起」（見本表第 7 列 044-0001 套用條）",
 ("123-0001","return.txt"): "判斷所指主詞錯置之病，現行已作「任由破戒者恣意受用並與在家人同共吃喝」；建議僅餘「十是→十」「深知時機合宜→善知時宜」等無關潤飾，不採用",
 ("259-0001","return.txt"): "判斷所指增譯「僧物／私自」現行已無（前批已修）；本批兩條建議反而含「私自供給」「私與僧中衣食」，與判斷相反，不採用（見 待議說明）",
 ("278-0004","return.txt"): "建議僅截取全段中「第七、破除不修道外道……」一句（另 700 餘字從缺），且現行該句已與建議逐字相同，無可套用",
 ("299-0004","return.txt"): "判斷所指「重物」現行已作「各類常住重物」；建議僅餘刪除段首【記文】標籤，屬體例倒退，不採用",
 ("08b_卷中之四-06","return.txt"): "判斷所指「自身行走在最下行」現行已作「自身位列在最下行」；建議僅餘刪「的／所／並」等無據改動，不採用",
 ("389-0001","return.txt"): "判斷所指「篇字若是」現行已作「從『篇』字以下分別辨析」；建議僅餘刪除段首【記文】標籤，不採用",
 ("160-0005","return.txt"): "判斷所指「非法／同師作損減」併為單一條件並增「為了破除非法」動機，現行已改為「或是…或是…」二開緣且無該增譯；建議僅餘「或是→若是」，無實質改善",
}
PENDING = set()

editmap = collections.defaultdict(list)
for (book, chunk, para, old, new, key, src, note) in EDITS:
    editmap[key].append((old, new, note))

def short(s, n=34):
    return s if len(s) <= n else s[:n] + "…"

out = []
n_apply = n_skip = n_pend = 0
for r in rows:
    base, src = r["base"], r["src"]
    loc = f'`{r["book"]}/{r["chunk"]}#{r["found"]}`'
    if r.get("moved"):
        loc += f'（原標 #{r["para"]}，偵測位移）'
    if base in APPLIED and (APPLIED[base] == "*" or APPLIED[base] == src):
        st = "套用"
        n_apply += 1
        if base == "459-0009":
            st = "套用（合併）"
            chg = "「龍鳥受苦」→「龍、鳥的事例」；「野干果報」→「野干之事」（二條各修一處，合併套用）"
        elif base == "217-0002":
            chg = "刪「酒兩〔註…〕」夾注並作「酒味」；另刪「𮒂果〔註…〕」夾注"
        elif base == "044-0001":
            chg = "「緣起」→「發戒之緣」（未採建議中之『《薩婆多論》』補注）"
        elif base == "205-0002":
            chg = "「自居上品」→「修持上品」（未採建議中「本來就沒有→本無」之潤飾）"
        elif base == "240-0003":
            chg = "「先遞上水，等那位比丘飲用之後」→「便遞上水，交給那位比丘之後」"
        elif base == "241-0006":
            chg = "「佛陀訓勉化導世人，都隨從正法的教訓」→「三鳥獸以此教化人民，人民都隨順其法訓」"
        elif base == "224-0001":
            chg = "「在樹上摘摸果實」→「在樹上以手觸摸果實」"
        elif base == "231-0005":
            chg = "「坐臥的地方」→「坐的地方」"
        else:
            parts = []
            for old, new, note in editmap[base]:
                parts.append(f"「{short(old)}」→「{short(new)}」")
            chg = "；".join(parts) if parts else "—"
        out.append((r["key"], loc, st, chg))
    elif (base, src) in PENDING:
        n_pend += 1
        out.append((r["key"], loc, "待議", "建議「常住僧團」仍保留判斷所指為誤之「常住」，未落實刪「常住」；應作「全部歸入僧團」"))
    else:
        n_skip += 1
        note = SKIPNOTE.get((base, src))
        if not note:
            note = "現行段與建議逐字相同（前批已套用）"
        out.append((r["key"], loc, "已相符跳過", note))

print("apply", n_apply, "skip", n_skip, "pend", n_pend, "total", len(out))
json.dump(out, open(r"AI語譯\_work\rows_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
