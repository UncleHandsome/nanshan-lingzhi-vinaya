# -*- coding: utf-8 -*-
"""資持記／行宗記 對映工具：共用函式。

核心：
- norm(): 只保留漢字，去除標點空白，避免標點差異干擾 n-gram。
- NoteIndex: 把記文建成 4-gram → 出現位置 的索引，並保留「字元位置 → 原行號」映射。
- best_window(): 在記文中找一段連續區間，使該區間涵蓋最多「相異」原文 4-gram。
"""
import os
import re
from bisect import bisect_right

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U0002ffff]")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def read_lines(p):
    with open(p, encoding="utf-8") as f:
        return f.read().splitlines()


def norm(s):
    return "".join(CJK_RE.findall(s))


def grams(s, n=4):
    """回傳 s 的相異 n-gram 集合。"""
    if len(s) < n:
        return set()
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def cover_ratio(orig_grams, note_text):
    """note_text 對 orig_grams 的覆蓋率（不計位置）。"""
    if not orig_grams:
        return 0.0
    return len(orig_grams & grams(norm(note_text))) / len(orig_grams)


class NoteIndex:
    """記文（單一檔）的 4-gram 位置索引，支援重疊率與行號定位。"""

    def __init__(self, path, n=4):
        self.path = path
        self.n = n
        self.raw = read(path)
        self.lines = self.raw.splitlines()
        # 字元位置 -> 行號（1 起）
        self._line_starts = []
        pos = 0
        for ln in self.lines:
            self._line_starts.append(pos)
            pos += len(ln) + 1
        self.norm_chars = []      # 正規化字元
        self.norm_pos = []        # 每個正規化字元在原檔的字元位置
        for i, ch in enumerate(self.raw):
            if CJK_RE.match(ch):
                self.norm_chars.append(ch)
                self.norm_pos.append(i)
        self.text = "".join(self.norm_chars)
        self.index = {}
        t = self.text
        for i in range(len(t) - n + 1):
            self.index.setdefault(t[i:i + n], []).append(i)

    def line_of_pos(self, pos):
        """正規化位置 -> 原檔行號（1 起）。"""
        if not self.norm_pos:
            return 0
        p = self.norm_pos[min(max(pos, 0), len(self.norm_pos) - 1)]
        return bisect_right(self._line_starts, p)

    def span_lines(self, a, b):
        """正規化區間 [a,b) -> (起始行, 結束行)。"""
        if b <= a:
            b = a + 1
        return self.line_of_pos(a), self.line_of_pos(b - 1)

    def hits(self, gset):
        """回傳 [(pos, gram)]，依 pos 排序。"""
        out = []
        idx = self.index
        for g in gset:
            for p in idx.get(g, ()):
                out.append((p, g))
        out.sort()
        return out

    def best_window(self, gset, width, lo=0, hi=None):
        """在 [lo,hi) 內找寬度 width 的視窗，最大化涵蓋的相異 gram 數。

        回傳 (covered, start, end, covered_set)；
        end 為視窗內最後一個命中位置 + n（不是 lo+width）。
        """
        if not gset:
            return 0, lo, lo, set()
        hi = len(self.text) if hi is None else hi
        hs = [(p, g) for (p, g) in self.hits(gset) if lo <= p < hi]
        if not hs:
            return 0, lo, lo, set()
        cnt = {}
        covered = 0
        best = (0, lo, lo, set())
        left = 0
        for right in range(len(hs)):
            p, g = hs[right]
            cnt[g] = cnt.get(g, 0) + 1
            if cnt[g] == 1:
                covered += 1
            # 收縮左界：保持 hs[right].pos - hs[left].pos < width
            while hs[right][0] - hs[left][0] >= width:
                gl = hs[left][1]
                cnt[gl] -= 1
                if cnt[gl] == 0:
                    del cnt[gl]
                    covered -= 1
                left += 1
            if covered > best[0]:
                cov_set = set(cnt.keys())
                start = hs[left][0]
                end = hs[right][0] + self.n
                best = (covered, start, end, cov_set)
        return best
