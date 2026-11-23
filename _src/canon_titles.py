# -*- coding: utf-8 -*-
"""行事鈔三十篇的共用短名／篇名格式（行事鈔、資持記、合編共用）。

網站上同一篇過去有三種寫法：
  行事鈔  `1 標宗顯德篇`
  資持記  `釋標宗篇`
  合編    `第1篇　標宗顯德`
本模組提供單一格式 `第N篇　短名`，續篇再加 `（續）` 或 `（續一）`。
"""
import re

# 1..30 短名（不含「篇」字，取通行篇目）
TITLES = {
    1: '標宗顯德',
    2: '集僧通局',
    3: '足數眾相',
    4: '受欲是非',
    5: '通辨羯磨',
    6: '結界方法',
    7: '僧網大綱',
    8: '受戒緣集',
    9: '師資相攝',
    10: '說戒正儀',
    11: '安居策修',
    12: '自恣宗要',
    13: '篇聚名報',
    14: '隨戒釋相',
    15: '持犯方軌',
    16: '懺六聚法',
    17: '二衣總別',
    18: '四藥受淨',
    19: '鉢器制聽',
    20: '對施興治',
    21: '頭陀行儀',
    22: '僧像致敬',
    23: '訃請設則',
    24: '導俗化方',
    25: '主客相待',
    26: '瞻病送終',
    27: '諸雜要行',
    28: '沙彌別行',
    29: '尼眾別行',
    30: '諸部別行',
}

# 資持記原典篇題（釋○篇）；只用於核對，顯示一律走 TITLES。
ZHICHI_TITLES = {
    1: '釋標宗篇', 2: '釋集僧篇', 3: '釋足數篇', 4: '釋受欲篇', 5: '釋羯磨篇',
    6: '釋結界篇', 7: '釋僧網篇', 8: '釋受戒篇', 9: '釋師資篇', 10: '釋說戒篇',
    11: '釋安居篇', 12: '釋自恣篇', 13: '釋篇聚篇', 14: '釋釋相篇',
    15: '釋持犯篇', 16: '釋懺六聚法篇', 17: '釋二衣篇', 18: '釋四藥篇',
    19: '釋鉢器篇', 20: '釋對施篇', 21: '釋頭陀篇', 22: '釋僧像篇',
    23: '釋訃請篇', 24: '釋導俗篇', 25: '釋主客篇', 26: '釋瞻病篇',
    27: '釋諸雜篇', 28: '釋沙彌篇', 29: '釋尼眾篇', 30: '釋諸部篇',
}

_CN = '一二三四五六七八九十'


def suffix(occ, total):
    """occ 為 1 起算的出現次序；total 為同篇在該書出現的總次數。"""
    if occ <= 1:
        return ''
    if total == 2:
        return '（續）'
    # 三次以上：續一、續二…
    n = occ - 1
    return '（續%s）' % (_CN[n - 1] if 1 <= n <= len(_CN) else str(n))


def label(num, occ=1, total=1):
    """`第N篇　短名` ＋續標記。num 必須在 1..30。"""
    return '第%d篇　%s%s' % (num, TITLES[num], suffix(occ, total))


RE_NUM_TITLE = re.compile(r'^\s*(\d+)\s*[\.．、]?\s*(.+?)篇?\s*$')


def parse_mark(text):
    """把生成器掃到的篇門字串解析成 (篇號, 短名)；解析不到回 None。

    接受 `1 標宗顯德篇`、`標宗顯德篇第1`、`第1篇 標宗顯德`、`1 毗尼大綱`。
    """
    s = (text or '').strip()
    m = re.match(r'^第?(\d+)篇?[\s　]*(.+?)$', s)
    if m:
        n, name = int(m.group(1)), m.group(2).strip()
    else:
        m = re.match(r'^(.+?)篇第([一二三四五六七八九十]+|\d+)$', s)
        if not m:
            return None
        name, cnum = m.group(1).strip(), m.group(2)
        n = _cn2int(cnum)
    name = re.sub(r'篇$', '', name).strip()
    if not (1 <= n <= 30) or not name:
        return None
    if name.startswith('釋') and name[1:] in TITLES.values():
        name = name[1:]
    return n, name


def _cn2int(s):
    s = (s or '').strip()
    if s.isdigit():
        return int(s)
    vals = {c: i for i, c in enumerate(_CN, 1)}

    def part(x):
        if not x:
            return 0
        if '十' in x:
            a, _b, b = x.partition('十')
            return (vals.get(a, 1) if a else 1) * 10 + vals.get(b, 0)
        return vals.get(x, 0)
    return part(s)
