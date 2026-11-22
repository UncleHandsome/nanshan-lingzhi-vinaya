# -*- coding: utf-8 -*-
"""定稿確定性正規化（不花 token）。

2026-11-22 再審指南強化：
  1. 開頭截除模型誤帶入的材料背景（【前文背景】【後文背景】…）。
  2. 引號狀態每段（空行）重置；引號內若「非原文逐字引用」，照樣套異體／簡體轉換
     （只豁免與 source 原字一致之被訓釋原詞）。
  3. 簡稱還原擴充（伽論／明了論／雜心／善生／成論／母論／見論／雜含／智論／五百問事）。
  4. 孤立單層『』統一轉「」。
  5. 新增 normalize_labeled()：雙欄（【疏文】【記文】）分欄各自對位原文化規，
     避免《母論》還原規則被另一欄的《毘尼母》關掉。
"""
import re


_VAR_FROM = ('煑竪虗汙竝説爲着衆盋鉢艸壍众问这为应经说义体归无时数却徧牀厨裏羣呪婬眞敎菓'
             '㭊鶴玅葢冐輭徤帀墻鬬襵')
_VAR_TO = ('煮豎虛污並說為著眾缽缽草塹眾問這為應經說義體歸無時數卻遍床廚裡群咒淫真教果'
           '析鶴妙蓋冒軟健匝牆鬥攝')
assert len(_VAR_FROM) == len(_VAR_TO), 'VAR_MAP 長度不一致'
VAR_MAP = str.maketrans(dict(zip(_VAR_FROM, _VAR_TO)))
URL_RE = re.compile(r'https?://[^\s）)」』】]+')
TAG_RE = re.compile(r'^\s*【(?:疏文|記文|鈔文|律文|註文|序文|記序)】\s*$')
_HAN_RE = re.compile(r'[^\u4e00-\u9fff]')

# 材料層背景區塊：模型偶爾整段照抄進譯文，先截掉（只取第一個區塊之前的正文）
BG_CUT_RE = re.compile(
    r'\n*\s*【(?:前文背景|後文背景|所釋鈔文|所釋疏文|本次待審[^】]*|待審譯文|'
    r'對照層[^】]*|跨段統一基準[^】]*|初審檢索摘錄[^】]*|必改硬傷|'
    r'資持記相關釋文|裁決檢索摘錄|原典雙行夾注|原典夾注|義鈔輔要記)[^】]*】')


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


# 簡稱還原：(展開式 pattern, 原文可能出現的標記, 保留簡稱)
_ABBR_RESTORE = (
    (re.compile(r'《薩婆多部[毘毗]尼摩得勒伽》'), ('摩得勒伽',), '伽論'),
    (re.compile(r'《摩得勒伽論》'), ('摩得勒伽',), '伽論'),
    (re.compile(r'《律二十二明了論》'), ('二十二',), '明了論'),
    (re.compile(r'《雜阿[毘毗]曇心論》'), ('雜阿毘曇心',), '雜心'),
    (re.compile(r'《(?:優婆塞戒經|善生經)》'), ('優婆塞戒', '善生經'), '善生'),
    (re.compile(r'《成實論》'), ('成實',), '成論'),
    (re.compile(r'《[毘毗]尼母[經論]》'), ('毘尼母',), '母論'),
    (re.compile(r'《雜阿含經》'), ('雜阿含',), '雜含'),
    (re.compile(r'《大智度論》'), ('大智度',), '智論'),
    (re.compile(r'《五百問(?:論|經|事)?》'), ('五百問事', '五百問經', '五百問論'), '五百問'),
    (re.compile(r'《五百問事(?:經)?》'), ('五百問事經',), '五百問事'),
)
# 《善見》系列獨立處理：依原文實際簡稱決定保留哪一種寫法
_ZHJ_RE = re.compile(r'《善見律[毘毗]婆沙》|《善見律》|《善見論》|《見論》|《善見》')


def _fix_shanjian(s, src_plain):
    if not src_plain:
        return s
    if '毘婆沙' in src_plain or '毗婆沙' in src_plain:
        target = '善見律毘婆沙'
    elif '善見律' in src_plain:
        target = '善見律'
    elif '善見論' in src_plain:
        target = '善見論'
    elif '見論' in src_plain:
        target = '見論'
    elif '善見' in src_plain:
        target = '善見'
    else:
        return s
    return _ZHJ_RE.sub('《%s》' % target, s)


def _cut_bg(text):
    """截掉材料背景區塊（只保留第一個背景標題之前的正文）。"""
    if not text:
        return text
    return BG_CUT_RE.split(text, maxsplit=1)[0]


def _strip_md(s):
    s = re.sub(r"(?m)^\s*#{1,6}\s+", "", s)
    s = s.replace(chr(42) * 2, "")
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

_VERNACULAR = re.compile(r'[的了著嗎呢吧這那們]')
_LAB_LINE = re.compile(r'^(【(?:疏文|記文|鈔文|律文|註文|序文|記序)】)\s*$')


def _plain_han(s):
    return _HAN_RE.sub('', s or '')


def _norm_line(s, src_plain, lab='鈔文'):
    """單行正規化；src_plain 已去標點並套 VAR_MAP。"""
    s = URL_RE.sub('', s)
    s = _strip_md(s)
    _parts = re.split(r'([「」『』])', s)
    _depth = 0
    for _i in range(len(_parts)):
        if _parts[_i] in ('「', '『'):
            _depth += 1
        elif _parts[_i] in ('」', '』'):
            _depth = max(0, _depth - 1)
        else:
            if _depth > 0:
                _qs = _parts[_i]
                for _qa, _qb in SIMP:
                    _qs = _qs.replace(_qa, _qb)
                _qs_norm = _plain_han(_qs).translate(VAR_MAP)
                _is_verbatim = bool(src_plain and len(_qs_norm) >= 1 and _qs_norm in src_plain)
                _conv = _qs.translate(VAR_MAP)
                if (not _is_verbatim) and (_conv != _qs) and (
                        len(_qs_norm) >= 6 or _VERNACULAR.search(_qs) or _conv != _qs):
                    _qs = _conv
                _parts[_i] = _qs
            if _depth == 0:      # 引號外：全轉（被訓釋原詞在引號內，不受影響）
                _seg = _parts[_i].translate(VAR_MAP)
                _seg = _seg.replace("头", "頭").replace("须发", "鬚髮").replace("须", "須").replace("鬓", "鬢")
                _seg = re.sub(r'(?<=[剃毛鬚须鬢鬓剪蓄束落青披削])[发發]', '髮', _seg)
                # 體例：此律／本律 → 《四分律》（引號內原詞不動；避開「律學／律宗」等複合詞）
                _seg = re.sub(r'(?<![《》根資日原])[此本]律(?![學宗門部制藏師條文典儀相家本意義])', '《四分律》', _seg)
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
    if src_plain:
        for _pat, _markers, _abbr in _ABBR_RESTORE:
            if not any(_m in src_plain for _m in _markers) and _abbr in src_plain:
                s = re.sub(r'(?:%s)?\s*%s' % (_abbr, _pat.pattern), '《%s》' % _abbr, s)
        s = _fix_shanjian(s, src_plain)
        if '毘尼毘婆沙' not in src_plain and '薩婆多毘尼' not in src_plain \
                and '毘婆沙' not in src_plain and '毗婆沙' not in src_plain:
            _cands = [x for x in ('婆沙', '婆論', '多論') if x in src_plain]
            if len(_cands) == 1:
                s = re.sub(r'(?:%s)?\s*《薩婆多[毘毗]尼[毘毗]婆沙》' % _cands[0], '《%s》' % _cands[0], s)
                if '薩婆多論' not in src_plain:
                    s = s.replace('《薩婆多論》', '《%s》' % _cands[0])
    s = re.sub(r'[（(]\s*[）)]', '', s)
    s = re.sub(r'^((?:\[\s*\d+\s*\]\s*)?)(?:提问|提問|問曰|问曰)\s*：', r'\1問：', s, flags=re.M)
    s = re.sub(r'^((?:\[\s*\d+\s*\]\s*)?)(?:回答|答曰|答云|答言)\s*：', r'\1答：', s, flags=re.M)

    for _a, _target in LABEL_FIX.items():
        if _a in s:
            s = s.replace(_a, _target or ('【%s】' % lab))
    s = re.sub(r'^(【(?:疏文|記文|鈔文|律文|註文|序文|記序)】)\s*(?=\S)', _tag_newline, s)
    s = re.sub(r'^((?:\[\s*\d+\s*\]\s*)?)(第[一二三四五六七八九十百千零〇\d]+篇[：:][^。\n]{1,20})。$',
               r'\1\2', s, flags=re.M)
    s = re.sub(r'\s+$', '', s)
    return s


def _normalize_body(text, src=''):
    text = _cut_bg(text)
    lab = '鈔文'
    for _cand in ('疏文', '記文', '律文', '註文', '序文', '記序'):
        if '【%s】' % _cand in text or '【%s（修訂）】' % _cand in text:
            lab = _cand
            break
    src_plain = _plain_han((src or '').translate(VAR_MAP)).replace('毗', '毘')
    lines = []
    for ln in text.split('\n'):
        if not ln.strip():
            # 空行＝段落界：重置引號深度，避免一個未閉合「」讓後文異體字轉換全失效
            lines.append('')
            continue
        lines.append(_norm_line(ln.rstrip(), src_plain, lab))
    out = '\n'.join(lines)
    out = re.sub(r'\n{3,}', '\n\n', out)
    return out


def normalize(text, src=''):
    out = _normalize_body(text, src).strip() + '\n'
    # 孤立單層『』（整段無成對外框「」）：統一轉「」
    if '「' not in out and '『' in out:
        out = out.replace('『', '「').replace('』', '」')
    return out


def normalize_labeled(text, by_lab, fallback_src=''):
    """雙欄譯文分欄正規化：每個【段別】各自以其原文作 src。

    by_lab：{段別: 原文}（同段別多段時可傳 list，會依序取用）。
    無標籤時退回整段 normalize(text, fallback_src)。
    """
    txt = _cut_bg(text or '')
    if not by_lab:
        return normalize(txt, fallback_src)
    _by = {}
    for _k, _v in by_lab.items():
        _by[_k] = list(_v) if isinstance(_v, (list, tuple)) else [_v]
    _parts = re.split(r'(?m)^(\s*【(?:疏文|記文|鈔文|律文|註文|序文|記序)】)\s*$', txt)
    if len(_parts) < 3:
        _parts2 = re.split(r'(【(?:疏文|記文|鈔文|律文|註文|序文|記序)】)', txt)
        if len(_parts2) < 2:
            return normalize(txt, fallback_src)
        _parts = [''] + _parts2
    out = []
    head = _parts[0].strip()
    if head:
        out.append(_normalize_body(head, fallback_src).strip())
    for i in range(1, len(_parts) - 1, 2):
        _tag = _parts[i]
        _name = re.sub(r'[【】\s]', '', _tag)
        _body = _parts[i + 1] if i + 1 < len(_parts) else ''
        _bucket = _by.get(_name) or []
        _src = _bucket.pop(0) if _bucket else ''
        _seg = _normalize_body(_tag.strip() + '\n' + _body, _src).strip()
        if _seg:
            out.append(_seg)
    res = '\n\n'.join(x for x in out if x.strip()) + '\n'
    if '「' not in res and '『' in res:
        res = res.replace('『', '「').replace('』', '」')
    return res
