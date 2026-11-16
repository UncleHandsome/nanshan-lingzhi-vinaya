# -*- coding: utf-8 -*-
"""共用書別設定：標籤、scope、輸出格式、專屬 note。"""
import os

BOOKS = ('業疏', '戒疏', '尼鈔', '行事鈔', '義鈔', '資持記')

NICAO_NOTE = ('《比丘尼鈔》多節略自《行事鈔》，查平行文可優先參看《行事鈔》《資持記》；'
               '惟須依比丘尼律制與對舉「僧／尼」語境審斷，不得以比丘制硬套覆蓋') 
CHOU_NOTE = '《行事鈔》《義鈔》為比丘律制，部別稱謂須與比丘眾相應'
JI_NOTE = ('《資持記》為《行事鈔》之記，記中「鈔」指《行事鈔》，「疏」指《業疏》，'
           '「文」指所牒《隨機羯磨》，「律」指《四分律》；《濟緣記》「疏」指《業疏》、'
           '《行宗記》「疏」指《戒疏》，記中「鈔云」不得解作《四分律》')
SHUJI_NOTE = ('《業疏》「文／注」指《隨機羯磨》，《戒疏》「文／注」指《含注戒本》，'
              '「律」方指《四分律》；記文之「疏云／鈔云／文云／注云」須依所釋之書判讀，'
              '且【疏】【記】須義理相契')

SHUJI_CTX = (
    '《業疏》所釋「文／注」指《隨機羯磨》文注，《戒疏》所釋指《含注戒本》文注，'
    '「律／本律」方指《四分律》；所牒「文／注」常即為【前文背景】中之【律】【註】段落，判讀時應優先向上對位；',
    '【疏】【記】須義理相契：疏文略語與典故須依記文確認指涉並保留銜接實詞，'
    '但不得將記文專論擴寫搬入疏文；記文釋義與科判動詞亦須受疏文前提約束；',
)

CFG = {
    '業疏': dict(unit='疏文', scope='疏文與記文', fmt='【疏文】……\n【記文】……',
                note=SHUJI_NOTE, ctx=SHUJI_CTX,
                shuji_ban='，亦勿將記文專論搬進疏文'),
    '戒疏': dict(unit='疏文', scope='疏文與記文', fmt='【疏文】……\n【記文】……',
                note=SHUJI_NOTE, ctx=SHUJI_CTX,
                shuji_ban='，亦勿將記文專論搬進疏文'),
    '尼鈔': dict(unit='鈔文', scope='鈔文', fmt='【鈔文】……', note=NICAO_NOTE, ctx=('', ''), shuji_ban=''),
    '行事鈔': dict(unit='鈔文', scope='鈔文', fmt='【鈔文】……', note=CHOU_NOTE, ctx=('', ''), shuji_ban=''),
    '義鈔': dict(unit='鈔文', scope='鈔文', fmt='【鈔文】……', note=CHOU_NOTE, ctx=('', ''), shuji_ban=''),
    '資持記': dict(unit='記文', scope='記文', fmt='【記文】……', note=JI_NOTE, ctx=('', ''), shuji_ban=''),
}


def book_of(path_or_text):
    """由批次路徑判斷書別。"""
    p = str(path_or_text)
    if '比丘尼鈔' in p or '尼鈔' in p:
        return '尼鈔'
    if '資持記' in p or '資持' in p:
        return '資持記'
    if '行事鈔' in p:
        return '行事鈔'
    if '拾毗尼' in p or '義鈔' in p:
        return '義鈔'
    if '戒疏' in p:
        return '戒疏'
    return '業疏'


def cfg(book):
    return CFG.get(book, CFG['業疏'])


def fmt_for(book, units=None):
    """依實際 units 的標籤決定輸出格式（單邊段只印該標籤）。"""
    labs = [u.get('lab') for u in (units or []) if u.get('lab')]
    if not labs:
        return cfg(book)['fmt']
    seen = []
    for lab in labs:
        if lab not in seen:
            seen.append(lab)
    if len(seen) == 1:
        return '【%s】……' % seen[0]
    return '\n'.join('【%s】……' % lab for lab in seen)
