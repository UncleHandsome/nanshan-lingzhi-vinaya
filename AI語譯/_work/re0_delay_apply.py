# -*- coding: utf-8 -*-
"""套用 存疑材料/待套用_re0.tsv 的延後條目到 AI語譯/out/03_業疏/*.txt

規則：
  * 只換 TSV 指定的那一段（段序 = 第 n 個非空段落 = split("\\n") 後 index 2n-2）
  * 其餘 byte 不動，保留原行尾（CRLF/LF）
  * 現行 == 新段落 -> ALREADY（已相符，不改）
  * 現行 != 新段落：
      - 兩者高度相似（difflib ratio >= 0.85，差異僅為零星字句）-> APPLY
      - 否則視為別人剛改過、內容衝突 -> CONFLICT（跳過並記錄）
  * 備份：歸檔/re0套用前/03_業疏/<chunk>_r.txt

用法： python re0_delay_apply.py dry | apply
"""
import csv, difflib, hashlib, os, shutil, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
os.chdir(ROOT)
TSV = os.path.join("存疑材料", "待套用_re0.tsv")
OUT = os.path.join("AI語譯", "out", "03_業疏")
BKDIR = os.path.join("歸檔", "re0套用前", "03_業疏")
MODE = sys.argv[1] if len(sys.argv) > 1 else "dry"
THRESH = 0.85

# ---------- 讀 TSV ----------
with open(TSV, encoding="utf-8", newline="") as f:
    recs = [r for r in csv.reader(f, delimiter="\t") if r and any(c.strip() for c in r)]
header, rows = recs[0], recs[1:]
assert header[:6] == ["段號", "書", "chunk", "段序", "新段落", "理由"], header
print(f"TSV header={header}  data_rows={len(rows)}")

# ---------- 檔案快取 ----------
files = {}
def load(chunk_key):
    if chunk_key in files:
        return files[chunk_key]
    cand = [fn for fn in os.listdir(OUT) if fn.endswith(".txt") and fn.startswith(chunk_key + "_")]
    assert len(cand) == 1, (chunk_key, cand)
    name = cand[0]
    path = os.path.join(OUT, name)
    with open(path, "rb") as fh:
        raw_bytes = fh.read()
    raw = raw_bytes.decode("utf-8")
    files[chunk_key] = dict(name=name, path=path, orig=raw, orig_bytes=raw_bytes,
                            lines=raw.split("\n"), sha_before=hashlib.sha256(raw_bytes).hexdigest())
    return files[chunk_key]

# ---------- 逐列判定 ----------
status = []
for r in rows:
    segid, book, chunk, para_s, new_p = r[0], r[1], r[2], r[3], r[4]
    reason = r[5] if len(r) > 5 else ""
    assert book == "03_業疏", (segid, book)
    f = load(chunk)
    para = int(para_s)
    idx = 2 * (para - 1)
    assert idx < len(f["lines"]) - 1, (segid, chunk, para, len(f["lines"]))
    line = f["lines"][idx]
    content = line[:-1] if line.endswith("\r") else line
    assert content.strip(), ("blank paragraph", segid, chunk, para)
    eol = line[len(content):]
    # 段序對應檢查：下一行應為空行
    assert idx + 1 >= len(f["lines"]) or f["lines"][idx + 1].rstrip("\r").strip() == "", \
        ("paragraph not followed by blank line", segid, chunk, para)
    sm = difflib.SequenceMatcher(None, content, new_p, autojunk=False)
    ratio = sm.ratio()
    edits = [(t, i1, i2, j1, j2) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
    if content == new_p:
        state = "ALREADY"
    elif ratio >= THRESH:
        state = "APPLY"
    else:
        state = "CONFLICT"
    status.append(dict(segid=segid, chunk=chunk, para=para, idx=idx, eol=eol,
                       old=content, new=new_p, new_raw=line, ratio=ratio,
                       edits=edits, state=state, reason=reason, file=f["name"]))

import collections
print("states:", dict(collections.Counter(s["state"] for s in status)))
for s in status:
    print(f'  {s["state"]:8s} {s["segid"]:<18s} {s["file"]} #{s["para"]:<3d} ratio={s["ratio"]:.4f} '
          f'oldlen={len(s["old"])} newlen={len(s["new"])} editops={len(s["edits"])}')

# 每段只改一次
pairs = [(s["chunk"], s["para"]) for s in status]
assert len(pairs) == len(set(pairs)), "duplicate (chunk,para) in TSV"
import itertools
for key, grp in itertools.groupby(sorted(pairs), key=lambda x: x[0]):
    print("  ", key, "target paras:", [p for _, p in grp])

if MODE == "dry":
    print("dry-run：未寫檔")
    sys.exit(0)

# ---------- 套用並寫檔 ----------
applied = [s for s in status if s["state"] == "APPLY"]
if not applied:
    print("nothing to write（全部已相符，未寫檔）")
    sys.exit(0)
by_file = collections.OrderedDict()
for s in applied:
    by_file.setdefault(s["chunk"], []).append(s)

os.makedirs(BKDIR, exist_ok=True)
backups = []
for chunk, grp in by_file.items():
    f = files[chunk]
    base = os.path.splitext(f["name"])[0]
    dst = os.path.join(BKDIR, base + "_r.txt")
    n = 2
    while os.path.exists(dst):
        with open(dst, "rb") as fh:
            if fh.read() == f["orig_bytes"]:
                break
        dst = os.path.join(BKDIR, f"{base}_r{n}.txt")
        n += 1
    if not os.path.exists(dst):
        shutil.copy2(f["path"], dst)
    with open(dst, "rb") as fh:
        assert fh.read() == f["orig_bytes"], ("backup mismatch", dst)
    backups.append(dst)
    print("backup:", dst)

for chunk, grp in by_file.items():
    f = files[chunk]
    for s in grp:
        f["lines"][s["idx"]] = s["new"] + s["eol"]
    out = "\n".join(f["lines"])
    assert out.count("\n") == f["orig"].count("\n"), ("newline count changed", chunk)
    with open(f["path"], "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    print("written:", f["path"])

# ---------- 驗證 ----------
print("\n=== 驗證 ===")
all_ok = True
for chunk, f in files.items():
    with open(f["path"], "rb") as fh:
        new_bytes = fh.read()
    new_raw = new_bytes.decode("utf-8")
    lines_b, lines_a = f["orig"].split("\n"), new_raw.split("\n")
    para_b = [l for l in lines_b if l.rstrip("\r").strip()]
    para_a = [l for l in lines_a if l.rstrip("\r").strip()]
    diff_idx = [i for i, (a, b) in enumerate(zip(lines_b, lines_a)) if a != b]
    expect = sorted(s["idx"] for s in status if s["chunk"] == chunk and s["state"] == "APPLY")
    exp_para = sorted(s["para"] for s in status if s["chunk"] == chunk and s["state"] == "APPLY")
    ok = (len(para_b) == len(para_a) and diff_idx == expect
          and len(diff_idx) == len(exp_para) and len(expect) == len(set(expect)))
    all_ok &= ok
    print(f'{chunk}: 段數 before={len(para_b)} after={len(para_a)} '
          f'| 相異行={len(diff_idx)} 實際套用={len(exp_para)} '
          f'| 行數 {len(lines_b)}->{len(lines_a)} | CRLF {f["orig"].count(chr(13)+chr(10))}->{new_raw.count(chr(13)+chr(10))} '
          f'| {"OK" if ok else "FAIL"}')
    # 每段只改一次：確認套用段落已等於新段落
    lines_now = new_raw.split("\n")
    for s in (x for x in status if x["chunk"] == chunk):
        cur = lines_now[s["idx"]].rstrip("\r")
        if s["state"] == "APPLY":
            assert cur == s["new"], ("post-verify failed", chunk, s["para"])
    print(f'   sha256 before={f["sha_before"][:16]} after={hashlib.sha256(new_bytes).hexdigest()[:16]}')

assert all_ok, "verification failed"
print("\nALL OK；TSV 資料列 =", len(status), " 套用 =", len(applied))
