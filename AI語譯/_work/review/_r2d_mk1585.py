# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2d_build as B

I = []
def e(seq, old, new, why): I.append((seq, old, new, why))
e(1, "就會生起過惱", "就會生起惱害", "過惱不成詞")
e(1, "法並沒有這種顧慮", "法並沒有這種道理", "顧慮為添加")
e(2, "更沒有任何方便可以構成別眾", "再沒有別的方便可以容許別眾", "律意是不許別眾，非無法構成")
e(2, "然而有情的心意在於通達和合", "然而僧情在於融通和合", "情指僧情，通和＝融通和合")
e(2, "隨其集會只要沒有乖違，才能成就法事", "隨所集人數而無乖違，方能成就法事", "關聯詞錯配")
e(3, "局限劃分為四個階位", "局限劃分為四位僧（四人、五人、十人、二十人）", "四位＝四位僧，非階位")
e(5, "加倍作白二", "加作白二", "加＝增羯磨遍數，非加倍")
e(5, "而加倍作白四", "而加作白四", "同上")
e(6, "第四、廣泛顯明合儀與非法", "第四、廣泛顯明足數與不足數（是與非）", "是非＝足數／不足數，非合法非法")
e(8, "即法依何處而生起", "即法依託處所（界）而起", "法依處起，非疑問")
e(14, "說戒、自恣、受戒，以及隨後五人以上的眾法", "說戒、自恣、受戒，乃至凡須五人以上所作的眾法", "隨宜屬下讀作乃至，非隨後")
e(16, "所以才稱作法度楷模", "所以說羯磨法有楷定的準則", "稱作／法度斷詞歧義")
e(17, "最終成就僧法是指對大眾宣說。", "最終成就僧法（原文此下為標點殘骸，文義待校）。", "原文亂碼，不得默補")
e(23, "在一一法之下歷經事、人、界來辨別通塞", "在一一法之下歷經人、事、界來辨別通塞", "依原文次序人、事、界")
V = [
  dict(seq=1, kind='真錯', reason='過惱、顧慮'),
  dict(seq=2, kind='真錯', reason='方便別眾、情、隨集無乖'),
  dict(seq=3, kind='真錯', reason='四位'),
  dict(seq=4, kind='誤報', reason='多重累加屬潤飾'),
  dict(seq=5, kind='真錯', reason='加非加倍'),
  dict(seq=6, kind='真錯', reason='是非＝足數'),
  dict(seq=7, kind='已修', reason='#34已作足數'),
  dict(seq=8, kind='真錯', reason='法依處起'),
  dict(seq=9, kind='誤報', reason='設法處所屬潤飾'),
  dict(seq=10, kind='誤報', reason='三種教法夾注'),
  dict(seq=11, kind='誤報', reason='通標屬潤飾'),
  dict(seq=12, kind='誤報', reason='元為眾法屬潤飾'),
  dict(seq=13, kind='誤報', reason='本制屬潤飾'),
  dict(seq=14, kind='真錯', reason='隨五人已去'),
  dict(seq=15, kind='誤報', reason='通塞用語統一'),
  dict(seq=16, kind='真錯', reason='楷模斷詞'),
  dict(seq=17, kind='真錯', reason='亂碼默補'),
  dict(seq=18, kind='誤報', reason='何意不合屬潤飾'),
  dict(seq=19, kind='誤報', reason='非界不通屬潤飾'),
  dict(seq=20, kind='誤報', reason='語序'),
  dict(seq=21, kind='存疑', reason='具緣是否篇名'),
  dict(seq=22, kind='誤報', reason='相攝通塞屬潤飾'),
  dict(seq=23, kind='真錯', reason='人事界次序'),
  dict(seq=24, kind='誤報', reason='條貫其相屬潤飾'),
]
B.make(1585, I, V)
