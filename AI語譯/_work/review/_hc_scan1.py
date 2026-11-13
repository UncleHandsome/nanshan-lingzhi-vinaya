# -*- coding: utf-8 -*-
import sys
import _hc_lib as L

needles = [
    u"大唐", u"言無寄", u"二十八", u"十八條", u"焉知", u"雀咽", u"圓籠",
    u"唐為", u"呼令反", u"呼合反", u"錯即是", u"火把", u"婆永", u"婆求",
    u"早救", u"自感", u"曰修", u"北名", u"闕婆", u"中衣", u"肅發", u"肅殺",
    u"略之", u"所引", u"十五日", u"十月五日", u"隨制", u"同濫", u"湯九", u"湯丸",
    u"遮部", u"道紀", u"由下", u"求魚", u"具玉", u"貝玉", u"通涶", u"肴書", u"看書",
    u"注撰", u"劫慮", u"皮質", u"反質", u"相又", u"寶即手", u"寶印手", u"寶手",
    u"通結", u"白和", u"千里", u"故承", u"陵尹", u"忉利", u"池沾", u"池沼",
    u"雜忽", u"四十", u"上起", u"憶志", u"後三日", u"缽", u"鉢",
]
for nd in needles:
    hits = L.grep_all(nd)
    print("=== %s : %d" % (nd, len(hits)))
    for c, i in hits[:40]:
        print("   ", c, i)
