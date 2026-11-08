# -*- coding: utf-8 -*-
import csv, io, json, re, sys

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
recs = json.load(open(BASE + r"\_qc_rows.json", encoding="utf-8"))


def parse_quoted(s, i):
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "「":
            depth += 1
        elif c == "」":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return None, i


def tokens(s):
    toks = []
    i = 0
    while i < len(s):
        if s[i] == "「":
            q, i2 = parse_quoted(s, i)
            if q is None:
                toks.append(["t", s[i:]])
                break
            toks.append(["q", q])
            i = i2
        else:
            j = i
            while j < len(s) and s[j] != "「":
                j += 1
            toks.append(["t", s[i:j]])
            i = j
    return toks


REPL_VERBS = {"改為", "改作", "改回", "改", "皆改為", "都改為", "應改為"}


def build_ops(sug):
    toks = tokens(sug)
    ops = []
    i = 0
    n = len(toks)
    while i < n:
        kind, val = toks[i]
        if kind != "q":
            i += 1
            continue
        prev = toks[i - 1][1] if i > 0 else ""
        # bracket swap: Q...外層「」改回〔〕
        if i + 1 < n and toks[i + 1][0] == "t":
            tail = toks[i + 1][1]
            if "改回〔〕" in tail and ("外層" in tail or "外之" in tail):
                ops.append({"kind": "bracket", "a": val})
                i += 2
                continue
        # delete
        if "刪" in prev:
            ops.append({"kind": "del", "a": val})
            i += 1
            continue
        # prepend
        if "補譯" in prev and ("開頭" in prev or "段首" in prev):
            ops.append({"kind": "prepend", "a": val})
            i += 1
            continue
        # replace
        if i + 2 < n and toks[i + 1][0] == "t" and toks[i + 2][0] == "q":
            verb = toks[i + 1][1].strip()
            if verb in REPL_VERBS:
                ops.append({"kind": "rep", "a": val, "b": toks[i + 2][1], "all": "皆" in verb or "都" in verb})
                i += 3
                continue
        i += 1
    return ops


def apply_ops(cur, ops):
    new = cur
    log = []
    for op in ops:
        if op["kind"] == "rep":
            a, b = op["a"], op["b"]
            cnt = new.count(a)
            if cnt == 0:
                log.append(("MISS", "rep", a[:30], 0))
                continue
            if op.get("all"):
                new = new.replace(a, b)
                log.append(("ok", "rep-all", a[:24], cnt))
            else:
                new = new.replace(a, b, 1)
                log.append(("ok", "rep", a[:24], cnt))
        elif op["kind"] == "del":
            a = op["a"]
            if a in new:
                new = new.replace(a, "", 1)
                log.append(("ok", "del", a[:24], 1))
            elif a + "。" in new:
                new = new.replace(a + "。", "", 1)
                log.append(("ok", "del+。", a[:24], 1))
            else:
                log.append(("MISS", "del", a[:30], 0))
        elif op["kind"] == "prepend":
            new = op["a"] + new
            log.append(("ok", "prepend", op["a"][:24], 1))
        elif op["kind"] == "bracket":
            a = op["a"]
            if "「" + a + "」" in new:
                new = new.replace("「" + a + "」", "〔" + a + "〕", 1)
                log.append(("ok", "bracket", a[:24], 1))
            else:
                log.append(("MISS", "bracket", a[:30], 0))
    return new, log


if __name__ == "__main__":
    out = []
    lines = []
    for d in recs:
        ops = build_ops(d["suggestion"])
        new, log = apply_ops(d["current"], ops)
        status = "OK" if ops and all(l[0] == "ok" for l in log) else ("NOOP" if not ops else "CHECK")
        lines.append("%-9s %-5s ops=%d %s" % (d["gid"], status, len(ops), log))
        if status == "OK":
            out.append({"gid": d["gid"], "book": d["book"], "chunk": d["chunk"], "seg": d["seg"], "new": new})
    open(BASE + r"\_qc_diag.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(out, open(BASE + r"\_qc_auto.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("auto ok:", len(out))
