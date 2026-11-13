# -*- coding: utf-8 -*-
"""四類關鍵句抽取：從 resp 抽含術語/主客/因果/範圍/經文等信號的句子。"""
import os, re, io, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
RESP = os.path.join(ROOT, "batch_qwen", "r7k")

KEY = re.compile(
    r"術語|名相|專名|詞義|訓義|名義|定義|釋義|義為|義即|讀反|譯反|反切|"
    r"三藏|戒體|作無作|止作|止犯|作持|通塞|廣教|略教|羯磨|波羅夷|僧殘|偷蘭|突吉羅|篇聚|"
    r"生造|自造|硬譯|照搬|"
    r"主語|主客|能所|主動|被動|對象|施受|自他|化他|指代|所指|回指|"
    r"因果|因位|果位|因中|果頭|倒果|修因|剋果|"
    r"範圍|窄化|偏窄|過寬|限定|全稱|一概|專指|統攝|含攝|兼通|通二|通局|"
    r"經文|律文|戒本|經處|本經|"
    r"顛倒|相反|剛好相反|正好相反|讀作|解作|解為|當作|視為|誤解|誤譯|"
    r"三寶|僧寶|比丘|沙彌|具足|"
    r"能|所"
)


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def clean(s):
    s = re.sub(r"\*\*|__|`", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def main(nums, width=220):
    w = int(width)
    for n in nums:
        p = os.path.join(RESP, "resp_%s.txt" % n)
        if not os.path.exists(p):
            print("\n===== resp_%s MISSING =====" % n)
            continue
        t = rd(p).replace("\r\n", "\n")
        print("\n===== resp_%s =====" % n)
        parts = re.split(r"【(\d{3,4}-\d{4})】", t)
        pre = clean(parts[0])
        # 前言只留最後 2 句（常含總結）
        if pre:
            sents = [s for s in re.split(r"(?<=。)|\n", pre) if s.strip()]
            print("[前言末] " + clean("".join(sents[-3:]))[:400])
        if len(parts) == 1:
            body = clean(t)
            hits = [s for s in re.split(r"(?<=。)", body) if KEY.search(s)]
            for h in hits:
                print("  · " + h[:w])
            continue
        for i in range(1, len(parts), 2):
            no, body = parts[i], clean(parts[i + 1])
            if not body:
                continue
            sents = [s for s in re.split(r"(?<=。)\s*|(?<=；)\s*", body) if s.strip()]
            hits = []
            for s in sents:
                if len(s) < 6:
                    continue
                if KEY.search(s):
                    hits.append(s[:w])
            if hits:
                print("\n-- " + no)
                for h in hits:
                    print("  · " + h)


if __name__ == "__main__":
    main(sys.argv[2:], sys.argv[1])

