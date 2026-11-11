# -*- coding: utf-8 -*-
"""Text-driven scan of current 02_戒疏 paragraphs for (D) repetition/redundancy."""
import io, os, re, json, collections

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")

STOP = set("""的 是 有 不 之 其 而 以 所 為 在 則 乃 並 又 即 皆 都 也 此 彼 我 他 若 如 因 故 從 於 與 及 或 無 得 能 可 應 當 已 未 非 一 二 三 四 五 六 七 八 九 十 百 千 萬 上 下 中 前 後 內 外 時 者 也 矣 焉 哉 乎 耳 則 曰 云 謂 名 者 今 昔 彼 此 何 誰 孰 然 亦 復 更 尚 猶 且 但 只 唯 又 還 就 便 卻 竟 終 始 自 共 相 互""".split())

def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps

chunks = sorted(f[:-4] for f in os.listdir(OUTD) if f.endswith(".txt") and f[:3] >= "09b")
rows = []
for ch in chunks:
    ps = paras(ch)
    for i, p in enumerate(ps):
        body = re.sub(r"^【[^】]*】", "", p)
        for sent in re.split(r"(?<=[。；！？])", body):
            s = sent.strip()
            if len(s) < 8: continue
            # candidate words: 2-char sequences
            words = re.findall(r"[\u4e00-\u9fff]{2}", s)
            cnt = collections.Counter(w for w in words if w not in STOP)
            rep = [(w, c) for w, c in cnt.items() if c >= 2]
            # same word non-overlapping repeats
            rep2 = []
            for w, c in rep:
                if len(re.findall(w, s)) >= 2:
                    rep2.append((w, len(re.findall(w, s))))
            if rep2:
                rows.append({"chunk": ch, "seg": i + 1, "sent": s, "rep": rep2})

json.dump(rows, io.open(os.path.join(HERE, "rep.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("paras/sents with repeat:", len(rows))
io.open(os.path.join(HERE, "rep.txt"), "w", encoding="utf-8").write(
    "\n".join("%s #%d %s | %s" % (r["chunk"][:3], r["seg"], ",".join("%s×%d" % w for w in r["rep"]), r["sent"][:160]) for r in rows))
print(collections.Counter(r["chunk"][:3] for r in rows).most_common(10))
