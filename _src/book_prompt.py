# -*- coding: utf-8 -*-
"""按書別渲染校對提示詞（共用骨架＋切換參數）。

模板：_src/review_prompt_v4_template.md
佔位：{BOOK_ID}、{AUTHORITY_CONTEXT}、{GENRE_RULES}
"""
import io
import os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TEMPLATE = os.path.join(B, '_src', 'review_prompt_v4_template.md')

# 鈔疏／律儀類：嚴禁夾譯夾疏
STRICT_RULES = '''【體例】
不可夾譯夾疏：不得將後代記文註解、別名考據、補充說明或評語塞入正文或括號中。'''

# 記文類：科判牒文、古注訓詁、破立立場三地雷；母本支架放寬
JI_RULES = '''【記文專用檢查】
1. 科判與牒文字頭（如「某下」「初中」「次」「後」）是否誤譯成一般詞彙，或指代母本段落錯位。
2. 字音訓詁術語（如「去呼」「合作某」「反切」「某，猶某也」）是否誤譯。
3. 本記正義與所破舊記（如「彼云」「古師」「舊記」）之立場是否混淆。
【體例放寬】
為使記文通順而簡明補出「所釋母本的關鍵詞句」（如指明「頓下」即指某句），屬必要翻譯支架，不視為夾註；惟不得額外塞入無關考據或現代發揮。'''

PROFILES = {
    'xingshichao': {
        'name': '行事鈔',
        'authority': '《資持記》等南山律疏、所引《四分律》本律',
        'rules': STRICT_RULES,
    },
    'jieshu': {
        'name': '戒本疏行宗記',
        'authority': '《行宗記》、《資持記》等靈芝記文、《四分律》本律',
        'rules': STRICT_RULES + '''
【自宗與異說】
注意道宣自宗立義與所引他部／舊師異說的起訖邊界，勿將他宗異說譯成自宗正義。''',
    },
    'yeshu': {
        'name': '業疏',
        'authority': '《濟緣記》、《資持記》等靈芝記文、《四分律》本律',
        'rules': STRICT_RULES + '''
【自宗與異說】
注意道宣自宗立義與所引他部／舊師異說的起訖邊界，勿將他宗異說譯成自宗正義。''',
    },
    'nicao': {
        'name': '尼鈔',
        'authority': '《四分律》比丘尼律藏、南山三大部（《行事鈔》《戒疏》《業疏》）及靈芝三記',
        'rules': STRICT_RULES + '''
【尼眾戒相】
特別留意比丘尼與比丘戒相異同（如八敬法、二部僧作法等）有無被誤套比丘通相。''',
    },
    'yichao': {
        'name': '義鈔',
        'authority': '《四分律》本律、南山三大部及靈芝三記',
        'rules': STRICT_RULES,
    },
    'zhichi': {
        'name': '資持記',
        'authority': '所釋母本《行事鈔》原文、《四分律》本律，及前後科判脈絡、《行宗記》《濟緣記》等輔釋',
        'rules': JI_RULES,
    },
}


def render_prompt(book_id, template_path=TEMPLATE):
    """回傳已代入 book_id／authority／genre_rules 的提示詞。"""
    if book_id not in PROFILES:
        raise KeyError('unknown book_id: %s（可用：%s）' % (book_id, ', '.join(PROFILES)))
    p = PROFILES[book_id]
    t = io.open(template_path, encoding='utf-8').read()
    return (t.replace('{BOOK_ID}', book_id)
             .replace('{AUTHORITY_CONTEXT}', p['authority'])
             .replace('{GENRE_RULES}', p['rules'])
             .strip() + '\n')


def main():
    import sys
    for bid in (sys.argv[1:] or PROFILES):
        print('=' * 20, bid, PROFILES[bid]['name'], '=' * 20)
        print(render_prompt(bid))
        print()


if __name__ == '__main__':
    main()
