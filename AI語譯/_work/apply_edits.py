# -*- coding: utf-8 -*-
"""存疑（return.txt / re2.txt）「是錯」條目套用器（冪等）

用法：
  python apply_edits.py dry            # 只檢查/預覽，不寫檔
  python apply_edits.py apply          # 套用「尚未套用」的條目，並備份
  python apply_edits.py apply 208-0001 053-0001   # 只處理指定條目

冪等規則（逐條）：
  * old 在目標段出現 1 次、new 尚未出現  -> 待套用
  * old 不存在、new 已存在            -> 視為已套用，跳過（不重複改）
  * 其他（找不到／出現多次／新舊皆無） -> 列為 PROBLEM，不動該檔
只有「有待套用條目」的檔案才會被寫入；備份同名者若內容與現行相同則沿用，
不同則加 _2/_3 後綴，絕不覆蓋既有備份。
"""
import os, sys, shutil, json
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join("AI語譯", "_work"))
from edits import EDITS

MODE = sys.argv[1] if len(sys.argv) > 1 else "dry"
ONLY = set(sys.argv[2:]) if len(sys.argv) > 2 else None
BKDIR = os.path.join("歸檔", "存疑套用前")

files = {}
def load(book, chunk):
    k = (book, chunk)
    if k not in files:
        p = os.path.join("AI語譯", "out", book, chunk + ".txt")
        raw = open(p, encoding="utf-8", newline="").read()
        files[k] = dict(path=p, orig=raw, lines=raw.split("\n"))
    return files[k]

status = []   # (key, state, book, chunk, para)
for (book, chunk, para, old, new, key, src, note) in EDITS:
    if ONLY and key not in ONLY:
        continue
    f = load(book, chunk)
    i = 2 * para - 2
    if i >= len(f["lines"]):
        status.append((key, "OOB", book, chunk, para)); continue
    line = f["lines"][i]
    cn = line.rstrip("\r")
    if cn.count(old) == 1:
        f["lines"][i] = cn.replace(old, new, 1) + line[len(cn):]
        status.append((key, "APPLY", book, chunk, para))
    elif old not in cn and new in cn:
        status.append((key, "ALREADY", book, chunk, para))
    else:
        status.append((key, "PROBLEM", book, chunk, para))

import collections
cnt = collections.Counter(s[1] for s in status)
print("edits:", len(status), dict(cnt))
for s in status:
    if s[1] in ("PROBLEM", "OOB"):
        print("  !!", s)

pending = collections.OrderedDict()
for key, st, book, chunk, para in status:
    if st == "APPLY":
        d = pending.setdefault((book, chunk), {"paras": [], "keys": []})
        if para not in d["paras"]:
            d["paras"].append(para)
        if key not in d["keys"]:
            d["keys"].append(key)

print("files with pending edits:", len(pending), "paragraphs:",
      sum(len(v["paras"]) for v in pending.values()))
for (book, chunk), v in sorted(pending.items()):
    print(f'  {book}/{chunk}  paras={sorted(v["paras"])}  keys={v["keys"]}')

if MODE == "dry":
    sys.exit(0)
if not pending:
    print("nothing to write（全部已套用）")
    sys.exit(0)

bkmade, bkreuse = [], []
for (book, chunk) in sorted(pending):
    f = files[(book, chunk)]
    d = os.path.join(BKDIR, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + ".txt")
    n = 2
    reuse = False
    while os.path.exists(dst):
        if open(dst, encoding="utf-8", newline="").read() == f["orig"]:
            reuse = True
            break
        dst = os.path.join(d, f"{chunk}_{n}.txt")
        n += 1
    if reuse:
        bkreuse.append(dst)
    else:
        shutil.copy2(f["path"], dst)
        bkmade.append(dst)

written = []
for (book, chunk) in sorted(pending):
    f = files[(book, chunk)]
    new = "\n".join(f["lines"])
    assert new.count("\n") == f["orig"].count("\n"), (book, chunk)
    assert "\r\n" not in new or new.count("\r\n") == new.count("\n"), (book, chunk)
    with open(f["path"], "w", encoding="utf-8", newline="") as fh:
        fh.write(new)
    written.append(f["path"])

print("new backups:", bkmade)
print("reused backups:", bkreuse)
print("written:", len(written))
for p in written:
    print("  ", p)
json.dump({"status": status, "written": written, "backups_new": bkmade, "backups_reused": bkreuse},
          open(os.path.join("AI語譯", "_work", "apply_log.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
