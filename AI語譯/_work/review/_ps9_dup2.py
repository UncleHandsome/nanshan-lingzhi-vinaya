# -*- coding: utf-8 -*-
"""收緊的重複掃描：同一段內相鄰 2-5 字內重複的二字詞（贅字候選）。"""
import re, os, glob

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(BASE, "AI語譯", "out", "資持記")
COV = ("01a", "01b", "01c", "01d", "01e", "01f", "02a")

STOP = set("""
的 了 是 在 而 以 於 其 之 也 有 不 為 所 者 則 故 又 若 此 即 非 無 如 從 由 因 當 已 皆 並 及 或 亦 乃 但 唯 更 再 可 能 得 將 已 相 自 他 我 汝 彼 諸 衆 眾 一 二 三 四 五 六 七 八 九 十 百 千 萬 上 下 中 前 後 內 外 大 小 多 少 高 低 輕 重 名 事 法 理 義 文 言 語 心 身 口 意 戒 律 罪 犯 持 行 持犯 篇 聚 門 科 段 句 字 云 謂 猶 即 皆 悉 咸 並 具 兼 通 別 總 正 邪 真 妄 虛 實 有無 得 失 開 遮 止 作 制 聽 稟 受 納 發 起 生 滅 斷 除 修 學 知 見 解 說 讀 誦 聽 聞 見 觀 察 檢 校 考 核 對 治 破 立 取 捨 與 奪 廢 興 存 沒 成 敗 得 失
""".split())

paras = []
for p in sorted(glob.glob(os.path.join(OUT, "*.txt"))):
    base = os.path.basename(p)
    if not any(base.startswith(f) for f in COV):
        continue
    chunk = os.path.splitext(base)[0]
    idx = 0
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if ln.strip():
            idx += 1
            paras.append((chunk, idx, ln.strip()))

res = []
for chunk, idx, t in paras:
    pos = {}
    for i in range(len(t) - 1):
        g = t[i:i+2]
        if not re.match(r"^[\u4e00-\u9fff]{2}$", g):
            continue
        pos.setdefault(g, []).append(i)
    for g, ps in pos.items():
        if g in STOP or len(g) != 2:
            continue
        for a, b in zip(ps, ps[1:]):
            d = b - a
            if 2 <= d <= 5:
                # 排除重疊（如 AABB / ABAB 的正常疊詞：上上、各各）
                if d == 2 and t[a] == t[a+1]:
                    continue
                res.append((chunk.split("_")[0], idx, g, t[max(0, a-12):min(len(t), b+14)]))
                break

seen = set()
with open(os.path.join(BASE, "AI語譯", "_work", "review", "_dup2.txt"), "w", encoding="utf-8") as f:
    for chunk, idx, g, ctx in sorted(res):
        k = (chunk, idx, g)
        if k in seen:
            continue
        seen.add(k)
        f.write("%s#%d [%s] %s\n" % (chunk, idx, g, ctx))
print("cases:", len(seen))
