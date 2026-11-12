# -*- coding: utf-8 -*-
"""Apply the 51 是錯 items to AI語譯/out/<書>/<chunk>.txt with backup + verification."""
import json, os, shutil, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BAK = os.path.join(ROOT, "歸檔", "末批套用前")
rows = json.load(open(os.path.join(HERE, "m2_rows.json"), encoding="utf-8"))

# 建議中與判斷無關的微差 → 還原為現行（只改問題處）
POST = {
    "1525-0001": [("而非從見聞而來", "而非從眼見耳聞而來")],
}

def read_bytes(p):
    with open(p, "rb") as f:
        return f.read()

def is_para(s):
    return bool(s.strip())

report = []
byfile = collections.OrderedDict()
for r in rows:
    byfile.setdefault(r["file"], []).append(r)

file_checks = []
for path, ents in byfile.items():
    raw = read_bytes(path)
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.split("\n")
    orig_paras = [l for l in lines if is_para(l)]
    eol_before = collections.Counter(("CRLF" if l.endswith("\r") else "LF") for l in orig_paras)

    book = ents[0]["book"]
    bdir = os.path.join(BAK, book)
    os.makedirs(bdir, exist_ok=True)
    chunk = os.path.basename(path)[:-4]
    bp = os.path.join(bdir, chunk + "_z.txt")
    if not os.path.exists(bp):
        shutil.copy2(path, bp)

    nz = [i for i, l in enumerate(lines) if is_para(l)]
    applied = 0
    for r in ents:
        li = nz[r["seg"] - 1]
        old = lines[li]
        sug = r["sug"]
        for a, b in POST.get(r["id"], []):
            sug = sug.replace(a, b)
        if old.rstrip("\r") == sug:
            r["result"] = "已相符"
        elif old.rstrip("\r") != r["cur"]:
            r["result"] = "衝突跳過"
        else:
            lines[li] = sug + ("\r" if old.endswith("\r") else "")
            r["result"] = "套用"
            applied += 1
        report.append(r)

    new = "\n".join(lines)
    new_lines = new.split("\n")
    new_paras = [l for l in new_lines if is_para(l)]
    eol_after = collections.Counter(("CRLF" if l.endswith("\r") else "LF") for l in new_paras)
    diff_nz = [k for k, (a, b) in enumerate(zip(orig_paras, new_paras)) if a != b]

    ok = (len(new_lines) == len(lines) and len(new_paras) == len(orig_paras)
          and eol_before == eol_after and applied == len(diff_nz))
    file_checks.append(dict(path=os.path.relpath(path, ROOT).replace("\\", "/"), book=book,
                            chunk=chunk, n_para_before=len(orig_paras),
                            n_para_after=len(new_paras), eol_before=dict(eol_before),
                            eol_after=dict(eol_after), applied=applied,
                            diff_paras=len(diff_nz), ok=ok))
    if not ok:
        print("!! VERIFY FAIL, not written:", path, file_checks[-1])
        continue
    data = new.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)

json.dump({"report": [{k: r[k] for k in ("id", "book", "chunk", "seg", "src", "result")}
                      for r in report],
           "files": file_checks},
          open(os.path.join(HERE, "m3_result.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

cnt = collections.Counter(r["result"] for r in report)
print(cnt)
print("files:", len(file_checks), "verify-fail:", sum(1 for f in file_checks if not f["ok"]))
print("applied total:", sum(f["applied"] for f in file_checks),
      "diff paras total:", sum(f["diff_paras"] for f in file_checks))
