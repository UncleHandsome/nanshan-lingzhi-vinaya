# -*- coding: utf-8 -*-
"""各書「篇目」判定與標籤規則（單一設定檔）"""
import re

N = '[一二三四五六七八九十]+'
RULES = {
    # 行事鈔：篇名獨立一行（可帶 ○◎【】）
    'xingshichao': dict(
        kind='line',
        pat=re.compile(r'^[○◎◯【]?\s*[\u4e00-\u9fff]{2,10}篇第' + N + r'[】]?$'),
        label='title', min_len=0),
    # 業疏：篇名夾在段落中
    'yeshu': dict(
        kind='search',
        pat=re.compile(r'[\u4e00-\u9fff]{2,8}篇第' + N),
        label='match', min_len=0),
    # 戒疏：戒名（【律】…戒。）
    'jieshu': dict(
        kind='search',
        pat=re.compile(r'^(?:【律】)?(?:[一二三四五六七八九十百]+、)?[\u4e00-\u9fff]{1,10}(?:戒|法|犍度)。?$'),
        label='strip', min_len=5),
    # 資持記：釋X篇
    'zhichi': dict(
        kind='search',
        pat=re.compile(r'釋[\u4e00-\u9fff]{2,6}篇'),
        label='match', min_len=0),
    # 尼鈔：篇名獨立一行
    'nicao': dict(
        kind='line',
        pat=re.compile(r'^[○◎◯【]?\s*[\u4e00-\u9fff]{2,10}篇第' + N + r'[】]?$'),
        label='title', min_len=0),
    # 義鈔：門名（短短一行）
    'yichao': dict(
        kind='line',
        pat=re.compile(r'^[\u4e00-\u9fff]{2,8}$'),
        label='title', min_len=0,
        deny=re.compile(r'^(將講|唐法寶|附|以上)')),
}

DROP_HEAD = re.compile(r'^【[律註疏記]】\s*')


def match(book, text):
    r = RULES.get(book)
    if not r:
        return False
    t = text.strip()
    if r.get('deny') is not None and r['deny'].search(t):
        return False
    if book == 'yeshu':
        # 目次型段落（同時列出多篇）不算篇名
        if len(re.findall(r'[\u4e00-\u9fff]{2,8}篇第[一二三四五六七八九十]+', t)) >= 2:
            return False
        # 篇名段落通常很短；過長的是目次或白話誤植
        if len(re.findall(r'[\u4e00-\u9fff]', t)) > 40:
            return False
    if book == 'jieshu':
        if t.startswith('【序】'):
            body = re.sub(r'^【序】\s*', '', t)
            return len(re.findall(r'[\u4e00-\u9fff]', body)) >= 6
        if t.startswith('【條目】'):
            return True
    if not r['pat'].search(t):
        return False
    if r['min_len']:
        t2 = DROP_HEAD.sub('', t).rstrip('。')
        if len(t2) < r['min_len']:
            return False
    return True


def label(book, text):
    r = RULES.get(book) or {}
    t = text.strip()
    if r.get('label') == 'match':
        m = r['pat'].search(t)
        return m.group(0) if m else t
    if book == 'jieshu':
        if t.startswith('【序】'):
            body = re.sub(r'^【序】\s*', '', t)
            return '序文：' + body[:10] + ('…' if len(body) > 10 else '')
        if t.startswith('【條目】'):
            m = re.search(r'○([\u4e00-\u9fff]{2,8}法)', t)
            return m.group(1) if m else '戒目'
    if r.get('label') == 'strip':
        t2 = DROP_HEAD.sub('', t).rstrip('。')
        return t2[:22] + ('…' if len(t2) > 22 else '')
    return t[:26] + ('…' if len(t) > 28 else '')


def is_line(book, text):
    """整行就是篇名（可只留標題、不必再印 pair）"""
    if not match(book, text):
        return False
    t = text.strip()
    lb = label(book, t)
    norm = lambda s: re.sub(r'[^\u4e00-\u9fff]', '', DROP_HEAD.sub('', s).rstrip('。'))
    return norm(t) == norm(lb)
