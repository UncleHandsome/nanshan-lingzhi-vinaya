# -*- coding: utf-8 -*-
"""定稿確定性正規化（不花 token）。"""
import re

VAR_MAP = str.maketrans('煑竪虗汙竝説爲着衆盋鉢艸壍众问这为应经说义体归无时数却徧牀厨裏羣呪婬眞敎菓', '煮豎虛污並說為著眾缽缽草塹眾問這為應經說義體歸無時數卻遍床廚裡群咒淫真教果')
URL_RE = re.compile(r'https?://[^\s）)」』】]+')
TAG_RE = re.compile(r'^\s*【(?:疏文|記文|鈔文|律文|註文|序文)】\s*$')


KNOWN_BOOKS = ('四分律', '五分律', '十誦律', '摩訶僧祇律', '善見律毘婆沙', '善見論', '薩婆多論', '毘尼母經', '善見律',
               '隨機羯磨', '行事鈔', '資持記', '業疏', '戒疏', '尼鈔', '義鈔',
               '濟緣記', '行宗記', '成實論', '成論', '婆沙', '雜心', '善生', '優婆塞戒經', '大般涅槃經', '梵網經',
               '律二十二明了論', '明了論',
               '薩婆多毘尼毘婆沙', '薩婆多部毘尼摩得勒伽', '摩得勒伽論',
               '婆論', '多論', '母論', '伽論', '四分比丘尼戒本',
               '大比丘三千威儀', '關中創立戒壇圖經', '中阿含經', '長阿含經',
               '瑜伽師地論', '雜阿毘曇心論', '增壹阿含經', '含注戒本', '四分僧戒本', '僧羯磨', '尼羯磨',
               '業疏科', '戒疏科', '行事鈔科', '義鈔科', '尼鈔科',
               '南山律學辭典', '行事鈔批', '根本說一切有部律', '含注戒本', '毘尼母經')


def _book_title(m):
    body = m.group(1)
    follow = m.group(2) or ''
    if body in KNOWN_BOOKS:
        return '《' + body + '》' + follow
    return '〈' + body + '〉' + follow


def _tag_newline(m):
    return m.group(1) + chr(10)


LABEL_FIX = {'【修訂譯文】': None, '【修正後譯文】': None, '【修正後的譯文】': None,
             '【鈔文（修訂）】': '【鈔文】', '【記文（修訂）】': '【記文】',
             '【疏文（修訂）】': '【疏文】', '【律文（修訂）】': '【律文】',
             '【註文（修訂）】': '【註文】', '【序文（修訂）】': '【序文】'}


_CC = None
try:
    import opencc as _occ
    _CC = None  # 停用 s2t：避免云→雲、斗→鬥等誤改
except Exception:
    _CC = None


_ABBR_RESTORE = (
    (re.compile(r'《[毘毗]尼母論》'), ('毘尼母',), '母論'),
    (re.compile(r'《善生經》'), ('優婆塞',), '善生'),
    (re.compile(r'《五百問事經》'), ('五百問事經',), '五百問事'),
    (re.compile(r'《善見論》'), ('善見論',), '見論'),
    (re.compile(r'《善見律(?:[毘毗]婆沙)?》'), ('善見',), '見論'),
    (re.compile(r'《薩婆多部[毘毗]尼摩得勒伽》'), ('摩得勒伽',), '伽論'),
    (re.compile(r'《律二十二明了論》'), ('二十二',), '明了論'),
    (re.compile(r'《雜阿[毘毗]曇心論》'), ('雜阿毘曇心',), '雜心'),
    (re.compile(r'《優婆塞戒經》'), ('優婆塞戒',), '善生'),
    (re.compile(r'《成實論》'), ('成實',), '成論'),
    (re.compile(r'《[毘毗]尼母經》'), ('毘尼母',), '母論'),
    (re.compile(r'《善見律(?:[毘毗]婆沙)?》'), ('毘婆沙', '善見律'), '善見'),
)

def _strip_md(s):
    s = re.sub(r"(?m)^\s*#{1,6}\s+", "", s)
    s = s.replace(chr(42)*2, "")
    s = s.replace('`', '')
    s = re.sub(r'(?m)^\s*[-*]\s+', '', s)
    s = re.sub(r'\[[^\]]*\]\(\)', '', s)
    return s


SIMP = (
    ('頭发', '頭髮'), ('头发', '頭髮'), ('白发', '白髮'), ('长发', '長髮'),
    ('结发', '結髮'), ('发爪', '髮爪'), ('发髻', '髮髻'),
    ('精准', '精準'),
    ('通达', '通達'),
    ('没有', '沒有'),
    ('时候', '時候'),
    ('这个', '這個'),
    ('那个', '那個'),
    ('我们', '我們'),
    ('他们', '他們'),
    ('什么', '什麼'),
    ('因为', '因為'),
    ('所以', '所以'),
    ('已经', '已經'),
    ('护', '護'), ('卫', '衛'), ('断', '斷'), ('灭', '滅'), ('广', '廣'), ('乐', '樂'), ('尽', '盡'), ('离', '離'),
    ('严', '嚴'), ('华', '華'), ('礼', '禮'), ('处', '處'), ('单', '單'),
    ('双', '雙'), ('该', '該'), ('当', '當'), ('传', '傳'), ('记', '記'), ('书', '書'), ('门', '門'),
    ('现在', '現在'),
    ('实际', '實際'),
    ('种种', '種種'),
    ('这样', '這樣'),
    ('那样', '那樣'),
    ('动作', '動作'),
    ('学习', '學習'),
    ('觉得', '覺得'),
    ('看见', '看見'),
    ('观察', '觀察'),
    ('认识', '認識'),
    ('讨论', '討論'),
    ('证明', '證明'),
    ('过来', '過來'),
    ('还是', '還是'),
    ('对于', '對於'),
    ('发现', '發現'),
    ('个人', '個人'),
    ('么', '麼'),
    ('颗', '顆'),
    ('达', '達'),
    ('没', '沒'),
    ('过', '過'),
    ('与', '與'),
    ('现', '現'),
    ('实', '實'),
    ('际', '際'),
    ('种', '種'),
    ('样', '樣'),
    ('动', '動'),
    ('学', '學'),
    ('觉', '覺'),
    ('见', '見'),
    ('观', '觀'),
    ('识', '識'),
    ('论', '論'),
    ('证', '證'),
    ('个', '個'),
    ('们', '們'),
    ('说', '說'),
    ('这', '這'),
    ('那', '那'),
    ('还', '還'),
    ('发', '發'),
    ('对', '對'),
    ('从', '從'),
    ('来', '來'),
)


def normalize(text, src=''):
    _lab = '鈔文'
    for _cand in ('疏文', '記文', '律文', '註文', '序文'):
        if '【%s】' % _cand in text or '【%s（修訂）】' % _cand in text:
            _lab = _cand
            break
    _depth = 0
    _src_plain = (src or '').translate(VAR_MAP).replace('毗', '毘')
    lines = []
    for ln in text.split('\n'):
        if not ln.strip():
            # 空行＝段落界：重置引號深度，避免一個未閉合「」讓後文異體字轉換全失效
            _depth = 0
            lines.append('')
            continue
        s = ln.rstrip()
        s = URL_RE.sub('', s)
        s = _strip_md(s)
        _parts = re.split(r'([「」『』])', s)
        for _i in range(len(_parts)):
            if _parts[_i] in ('「', '『'):
                _depth += 1
            elif _parts[_i] in ('」', '』'):
                _depth = max(0, _depth - 1)
            else:
                if _depth > 0:
                    # 引號內仍轉現代簡體字（不處理異體／古字）
                    _qs = _parts[_i]
                    for _qa, _qb in SIMP:
                        _qs = _qs.replace(_qa, _qb)
                    _parts[_i] = _qs
                if _depth == 0:      # 引號內保留原字（被訓釋原詞、引文）
                    _seg = _parts[_i].translate(VAR_MAP)
                    _seg = _seg.replace("头", "頭").replace("须发", "鬚髮").replace("须", "須").replace("鬓", "鬢")
                    _seg = re.sub(r'(?<=[剃毛鬚须鬢鬓剪蓄束落青披削])[发發]', '髮', _seg)
                    if _CC:
                        _seg = _CC.convert(_seg)
                    for _a, _b in SIMP:
                        _seg = _seg.replace(_a, _b)
                    _parts[_i] = _seg
        s = ''.join(_parts)
        s = re.sub(r'〈([^〈〉《》]{1,20})〉(篇|品|章|節|門|科|犍度|境|體|軌)?', _book_title, s)
        s = re.sub(r'《([^《》〈〉]{1,12}(?:篇|品|章|節|門|犍度))》', r'〈\1〉', s)
        s = re.sub(r'《(四分|十誦|五分|僧祇)(?!律)》', r'《\1律》', s)
        s = s.replace('《摩訶僧祇》', '《摩訶僧祇律》')
        if _src_plain:
            for _pat, _markers, _abbr in _ABBR_RESTORE:
                if not any(_m in _src_plain for _m in _markers) and _abbr in _src_plain:
                    s = re.sub(r'(?:%s)?\s*%s' % (_abbr, _pat.pattern), '《%s》' % _abbr, s)
            if '毘尼毘婆沙' not in _src_plain and '薩婆多毘尼' not in _src_plain:
                _cands = [x for x in ('婆沙', '婆論', '多論') if x in _src_plain]
                if len(_cands) == 1:
                    s = re.sub(r'(?:%s)?\s*《薩婆多[毘毗]尼[毘毗]婆沙》' % _cands[0], '《%s》' % _cands[0], s)
                    if '薩婆多論' not in _src_plain:
                        s = s.replace('《薩婆多論》', '《%s》' % _cands[0])
        s = re.sub(r'[（(]\s*[）)]', '', s)
        s = re.sub(r'^((?:\[\s*\d+\s*\]\s*)?)(?:提问|提問|問曰|问曰)\s*：', r'\1問：', s, flags=re.M)
        s = re.sub(r'^((?:\[\s*\d+\s*\]\s*)?)(?:回答|答曰|答云|答言)\s*：', r'\1答：', s, flags=re.M)

        for _a, _target in LABEL_FIX.items():
            if _a in s:
                s = s.replace(_a, _target or ('【%s】' % _lab))
        s = re.sub(r'^(【(?:疏文|記文|鈔文|律文|註文|序文)】)\s*(?=\S)', _tag_newline, s)
        s = re.sub(r'^((?:\[\s*\d+\s*\]\s*)?)(第[一二三四五六七八九十百千零〇\d]+篇[：:][^。\n]{1,20})。$',
                   r'\1\2', s, flags=re.M)
        s = re.sub(r'\s+$', '', s)
        lines.append(s)
    out = '\n'.join(lines)
    out = re.sub(r'\n{3,}', '\n\n', out)
    return out.strip() + '\n'
