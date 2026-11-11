# -*- coding: utf-8 -*-
"""Robust extraction of old→new edit pairs from 建議 text."""
import re

META = ('原文', '其餘', '照原譯', '照原', '不改', '暫不', '待查', '或改', '建議', '應作', '應改')

def _clean(x):
    x = x.strip().strip('，。；、 ')
    x = x.replace('**', '')
    return x

def parse_arrow(sugg):
    """Return list of (old, new) pairs, filtered and de-overlapped."""
    if not sugg:
        return []
    s = sugg.replace('**', '')
    pairs = []
    # 「A」→「B」
    for m in re.finditer(r'「([^」]{1,90})」\s*[→➜]\s*「([^」]{0,90})」', s):
        pairs.append((m.group(1), m.group(2)))
    for m in re.finditer(r'「([^」]{1,90})」\s*[→➜]\s*([^\s「」。；，]{1,80})', s):
        pairs.append((m.group(1), m.group(2)))
    # 「A」改為「B」 etc (B quoted)
    for m in re.finditer(r'「([^」]{1,90})」\s*(?:改為|改作|改成|改成|換作|換為)\s*「([^」]{0,90})」', s):
        pairs.append((m.group(1), m.group(2)))
    # 「A」改為B（unquoted, short）
    for m in re.finditer(r'「([^」]{1,90})」\s*(?:改為|改作|改成)\s*([^\s「」。；，]{1,40})', s):
        pairs.append((m.group(1), m.group(2)))
    # 刪除「A」
    for m in re.finditer(r'刪(?:除|去|掉)?\s*「([^」]{1,90})」', s):
        pairs.append((m.group(1), ''))

    out = []
    for old, new in pairs:
        old = _clean(old); new = _clean(new)
        if not old or len(old) < 1:
            continue
        if any(k == old[:2] and len(old) <= 6 for k in META):
            continue
        if any(k in old for k in ('原文作', '原文', '刪', '→', '其餘', '照原')):
            continue
        if any(k in new for k in ('原文作', '其餘照原', '照原譯', '刪)', '→')):
            continue
        if new in ('（刪）', '(刪)', '刪', '刪除'):
            new = ''
        out.append((old, new))
    # de-overlap: drop pair whose old is contained in another pair's old
    keep = []
    for i, (o, n) in enumerate(out):
        if any(j != i and o in out[j][0] and len(out[j][0]) > len(o) for j in range(len(out))):
            continue
        keep.append((o, n))
    # dedupe
    seen = set(); res = []
    for p in keep:
        if p not in seen:
            seen.add(p); res.append(p)
    return res
