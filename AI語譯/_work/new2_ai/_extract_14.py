# -*- coding: utf-8 -*-
"""Extract 鈔序 -> 記序 mapping from 篇14.txt (工作表 14 清冊)."""
import json, os, re

src = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\new2_sec\篇14.txt"
dst = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\new2_ai\out_篇14.json"

rows = []
skipped = []
with open(src, encoding="utf-8") as f:
    for ln, line in enumerate(f, 1):
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        c_chao, c_ji = cells[0], cells[2]

        # header / separator rows
        if "鈔序" in c_chao or set(c_chao.replace("*", "").strip()) <= set("-: "):
            continue

        raw_chao = c_chao.replace("*", "").strip()
        raw_ji = c_ji.replace("*", "").strip()
        if not raw_chao or not raw_ji:
            skipped.append((ln, raw_chao, raw_ji, "empty"))
            continue

        if any(k in raw_chao for k in ("篇前", "開卷", "篇題")):
            chao = 0
        else:
            m = re.search(r"\d+", raw_chao)
            if not m:
                skipped.append((ln, raw_chao, raw_ji, "no chao num"))
                continue
            chao = int(m.group())

        # ji cell: multiple segments?
        segs = [x for x in re.split(r"[、,，;；]|＋|\+", raw_ji) if x.strip()]
        whole_sheet = re.search(r"Sheet\s*(\d+)", "|".join(cells), re.I)

        nums = [int(x) for x in re.findall(r"\d+", raw_ji)]
        if not nums:
            skipped.append((ln, raw_chao, raw_ji, "no ji num"))
            continue
        ji_from, ji_to = nums[0], nums[-1]
        if ji_from > ji_to:
            ji_from, ji_to = ji_to, ji_from
        sheet = int(whole_sheet.group(1)) if whole_sheet else 0

        note = ""
        if len(segs) > 1:
            note = "multi-seg cell: " + raw_ji
        if raw_chao != str(chao):
            note = (note + " | " if note else "") + f"chao cell: {raw_chao}"

        rows.append({"chao": chao, "ji_from": ji_from, "ji_to": ji_to, "sheet": sheet,
                     "_ln": ln, "_chao": raw_chao, "_ji": raw_ji, "_note": note})

os.makedirs(os.path.dirname(dst), exist_ok=True)
body = ",\n".join(
    '{"chao":%d,"ji_from":%d,"ji_to":%d,"sheet":%d}'
    % (r["chao"], r["ji_from"], r["ji_to"], r["sheet"]) for r in rows
)
with open(dst, "w", encoding="utf-8", newline="\n") as f:
    f.write('{"rows":[\n' + body + "\n]}\n")

print("rows:", len(rows), "skipped:", skipped)
prev = 0
for r in rows:
    flag = ""
    if r["ji_from"] < prev:
        flag = "  <<< BACKWARD"
    prev = max(prev, r["ji_to"])
    print(f'{r["_ln"]:4d} chao={r["chao"]:4d} ji={r["ji_from"]:4d}-{r["ji_to"]:4d} '
          f'sheet={r["sheet"]}  cell=[{r["_chao"]}] [{r["_ji"]}]{flag}')
    if r["_note"]:
        print("        NOTE:", r["_note"])
