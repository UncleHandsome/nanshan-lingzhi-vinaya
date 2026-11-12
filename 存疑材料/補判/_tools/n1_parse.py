# -*- coding: utf-8 -*-
"""Step 1 (v2): parse r2/r3 存疑 items + verdict-key index."""
import os, re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

# ---------------- verdict files (already judged) ----------------
VERDICT = [
    os.path.join(SU, "re0.txt"),
    os.path.join(ROOT, "歸檔", "complex_存疑_已裁決", "complex_存疑", "return.txt"),
    os.path.join(ROOT, "歸檔", "complex_存疑_已裁決", "complex_存疑", "re2.txt"),
    os.path.join(ROOT, "歸檔", "complex_存疑_已裁決", "complex_存疑", "re3.txt"),
]
H = re.compile(r"^#{2,4} +(.+?)[｜|](是錯|不是錯|材料不足|應改|不應改)\s*$", re.M)
def full_ids(s):
    return re.findall(r"(?<!\d)(\d{3,4})-(\d{4})(?!\d)", s)
def base_id(s):
    fi = full_ids(s)
    if fi:
        return fi[0][0] + "-" + fi[0][1]
    m = re.search(r"(?<!\d)(\d{3,4})(?!\d)", s)
    return m.group(1) if m else None

judged, judged_base = {}, {}
for p in VERDICT:
    if not os.path.exists(p):
        print("MISSING:", p); continue
    n = 0
    for m in H.finditer(rd(p)):
        key, v = m.group(1).strip(), m.group(2)
        for a, b in full_ids(key):
            judged_base[a + "-" + b] = v
            judged[f"{a}-{b}"] = v
        n += 1
    print(f"{os.path.basename(p):12s} verdicts={n}  baseids={len(judged_base)}")
print("distinct base ids judged:", len(judged_base))

# ---------------- 段號 index from 校閱 splits ----------------
HDR = re.compile(r"^【(\d{3,4}-\d{4})】 *(.+)$", re.M)
seg_index, loc_index = {}, {}
for sub in ("校閱_10K", "校閱_20K", "校閱_40K"):
    d = os.path.join(ROOT, sub)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        for m in HDR.finditer(rd(os.path.join(d, fn))):
            key, loc = m.group(1), m.group(2).strip()
            mm = re.match(r"^(.+?)/([^#]+)#(\d+)", loc)
            if not mm:
                continue
            rec = {"book": mm.group(1), "chunk": mm.group(2), "seg": int(mm.group(3)), "src": sub}
            seg_index.setdefault(key, rec)
            loc_index.setdefault((rec["book"], rec["chunk"], rec["seg"]), key)
print("seg_index", len(seg_index), "loc_index", len(loc_index))

file_index = {}
for k in seg_index:
    file_index.setdefault(k.split("-")[0], []).append(k)

# ---------------- parse 存疑 files ----------------
FILE_META = {"01_行事鈔": "01_行事鈔", "02_戒疏": "02_戒疏", "03_業疏": "03_業疏",
             "04_比丘尼鈔": "04_比丘尼鈔", "05_拾毗尼義鈔": "05_拾毗尼義鈔",
             "資持記": "資持記", "其他三書": None}
FIELD = {"原文", "現譯", "譯文", "理由", "Qwen 主張", "未改理由", "待查", "判斷",
         "說明", "依據", "建議", "問題", "原文（#19）", "今譯"}
CHUNKHINT = re.compile(r"([0-9]{2}[a-z]|00_卷首)[_\u4e00-\u9fff]{0,8}\s*(?:#|＃)\s*(\d+)")

items = []
for sub in ("r2_存疑", "r3_存疑"):
    d = os.path.join(SU, sub)
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"):
            continue
        book_guess = FILE_META.get(fn[:-3])
        cur = [None]
        section = [""]
        def flush():
            if cur[0] and (cur[0]["body"].strip() or cur[0]["raw"].strip()):
                cur[0]["body"] = re.sub(r"\n{3,}", "\n\n", cur[0]["body"]).strip()
                items.append(cur[0])
            cur[0] = None
        for ln in rd(os.path.join(d, fn)).split("\n"):
            s = ln.rstrip()
            if not s.strip():
                if cur[0]:
                    cur[0]["body"] += "\n"
                continue
            is_h2 = s.startswith("## ")
            is_num = re.match(r"^\d+\.\s", s) is not None
            is_bul = s.startswith("- **") or s.startswith("* **")
            body_txt = s.lstrip("#").strip()
            mb = re.match(r"^-\s*\*\*([^*]+)\*\*(.*)$", body_txt)
            fld = mb.group(1).strip().rstrip("：:") if mb else None
            if is_bul and fld in FIELD:
                if cur[0] is None:
                    continue
                cur[0]["body"] += mb.group(1) + "：" + mb.group(2).lstrip("：:") + "\n"
                for q in re.findall(r"「([^」]{1,40})」", s):
                    if q not in cur[0]["quotes"]:
                        cur[0]["quotes"].append(q)
                continue
            if is_h2 or is_num or is_bul:
                hdr_txt = re.sub(r"^\d+\.\s*", "", body_txt)
                hdr_txt = re.sub(r"^-\s*", "", hdr_txt)
                if is_h2 and not (full_ids(hdr_txt) or CHUNKHINT.search(hdr_txt)
                                  or "「" in hdr_txt or "材料" in hdr_txt):
                    flush(); section[0] = body_txt; continue
                flush()
                cur[0] = {"raw": hdr_txt, "body": "", "src": f"{sub}/{fn}",
                          "book_guess": book_guess, "section": section[0],
                          "quotes": re.findall(r"「([^」]{1,40})」", hdr_txt)}
                ch = CHUNKHINT.search(hdr_txt)
                if ch:
                    cur[0]["chunk_hint"] = ch.group(1)
                    cur[0]["seg_hint"] = int(ch.group(2))
                continue
            if cur[0] is None:
                continue
            cur[0]["body"] += s + "\n"
            for q in re.findall(r"「([^」]{1,40})」", s):
                if q not in cur[0]["quotes"]:
                    cur[0]["quotes"].append(q)
        flush()

print("raw items", len(items))

# ---------------- derive locatable ids (split multi-id items) ----------------
def norm_raw(s):
    s = re.sub(r"(?<!\d)(\d{3,4})\*\*[：:]\s*(\d{4})", r"\1-\2", s)   # 225**：0001
    s = re.sub(r"[／/](?=\d{4}\b)", "、", s)
    return s

out = []
for it in items:
    raw = norm_raw(it["raw"])
    it["raw"] = raw
    fi = full_ids(raw)
    ch = CHUNKHINT.search(raw)
    if fi:
        ids = []
        for a, b in fi:
            k = a + "-" + b
            if k not in ids:
                ids.append(k)
        it["ids"] = ids
        it["resolve"] = "seg"
        it["files"] = []
    elif ch:
        it["ids"] = []
        it["resolve"] = "chunk"
        it["files"] = []
    else:
        m = re.search(r"(?<!\d)(\d{3,4})(?!\d)", raw)
        it["ids"] = []
        it["files"] = [m.group(1)] if m else []
        it["resolve"] = "file" if m else "quote"
    # split
    if it["resolve"] == "seg" and len(it["ids"]) > 1:
        for k in it["ids"]:
            c = dict(it); c["ids"] = [k]; c["siblings"] = [x for x in it["ids"] if x != k]
            out.append(c)
    else:
        out.append(it)
items = out
from collections import Counter
print("after split", len(items), Counter(i["resolve"] for i in items))

json.dump({"items": items, "judged_base": judged_base, "seg_index": seg_index,
           "loc_index": {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in loc_index.items()}},
          open(os.path.join(TOOLS, "n1_parsed.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("\n--- seg samples ---")
for it in [x for x in items if x["resolve"] == "seg"][:5]:
    print(" ", it["ids"], repr(it["raw"][:80]))
print("--- chunk samples ---")
for it in [x for x in items if x["resolve"] == "chunk"][:8]:
    print(" ", it.get("chunk_hint"), it.get("seg_hint"), repr(it["raw"][:80]))
print("--- file samples ---")
for it in [x for x in items if x["resolve"] == "file"][:8]:
    print(" ", it["files"], repr(it["raw"][:80]))
print("--- quote samples ---")
for it in [x for x in items if x["resolve"] == "quote"][:8]:
    print(" ", repr(it["raw"][:80]))
