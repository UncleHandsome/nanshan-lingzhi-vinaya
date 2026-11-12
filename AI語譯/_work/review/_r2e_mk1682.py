# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1682
items = [
 (46, '隨由僧中主事之人予以指定處分', '隨由一人予以指定處分即可', '隨人處分=任一人，非僧中主事'),
 (48, '大小便處（廁所）又在西南面', '大小便處（廁所）更在廚房的西南方', '又西南=更在廚後'),
 (48, '隨其應允之語即告作成', '隨他所說之語便得成就', '應允為添義'),
 (48, '如果是村落中的老宿施主，召他前來遣令他作指定', '如果是村落中的耆老，就召他前來令其作淨', '老宿非施主；遣作=令作淨'),
 (49, '就召喚其父輩長者', '就召喚村中的父老耆宿', '父宿=父老耆宿'),
 (54, '僧俗二眾的居處若都荒廢滿二年', '僧眾住處與俗人住處若都荒廢滿二年', '兩住=僧住處與俗住處'),
 (57, '後三種是就自身之處辨明淨地', '後三種是就僧自有之物辨明淨地', '自=自物，非自身'),
 (58, '第四門辨明周遍與殘缺', '第四門辨明院相周匝與殘缺', '周=院相周匝'),
 (64, '處分是由個人加持', '處分是由個人加法', '加持非律語，加=加法'),
 (64, '羯磨是大眾僧法，隨所作之事的遠近而定', '羯磨是大眾僧法，隨事情時間的久近都可作', '隨事遠近=通久近'),
 (65, '同樣制定不得超過時限', '兩律都規定不得超過時限', '竝=兩律皆'),
 (66, '處分隨時只要少數或多數人即可，羯磨則必須在四人以上',
      '處分則隨時人多人少皆可，羯磨則必須至少四人', '少多=人多人少；已上含四人'),
]
verdicts = [
 dict(ref=49,kind='真錯',reason='父宿=父老耆宿'),
 dict(ref=48,kind='真錯',reason='老宿非施主、遣作'),
 dict(ref=48,kind='真錯',reason='隨語不添應允'),
 dict(ref=48,kind='誤報',reason='捉柱譯法統一屬體例'),
 dict(ref=48,kind='誤報',reason='處分補指定屬體例'),
 dict(ref=48,kind='真錯',reason='又西南層遞'),
 dict(ref=54,kind='真錯',reason='僧俗兩住'),
 dict(ref=57,kind='真錯',reason='自=自物'),
 dict(ref=58,kind='真錯',reason='周=院相周匝'),
 dict(ref=55,kind='誤報',reason='何有非疑譯文可通'),
 dict(ref=55,kind='誤報',reason='三四兩門照字面可'),
 dict(ref=64,kind='真錯',reason='加持=加法'),
 dict(ref=64,kind='真錯',reason='隨事遠近'),
 dict(ref=65,kind='真錯',reason='竝=兩律'),
 dict(ref=65,kind='誤報',reason='并/並異體'),
 dict(ref=65,kind='誤報',reason='五處六法承前可'),
 dict(ref=65,kind='誤報',reason='居土出校屬校勘'),
 dict(ref=64,kind='誤報',reason='言羯磨通名照譯可'),
 dict(ref=66,kind='真錯',reason='少多、已上'),
 dict(ref=46,kind='真錯',reason='隨人處分'),
 dict(ref=46,kind='誤報',reason='壅結潤飾'),
 dict(ref=46,kind='誤報',reason='處分淨解說屬加註'),
 dict(ref=56,kind='誤報',reason='列數譯文可'),
 dict(ref=53,kind='已修',reason='out作判釋，材作判決'),
 dict(ref=47,kind='誤報',reason='嚴淨=莊嚴清淨已合'),
 dict(ref=50,kind='已修',reason='out已有大眾和合相通'),
 dict(ref=51,kind='已修',reason='out作不是其他外物'),
 dict(ref=59,kind='已修',reason='out已有如法作法'),
 dict(ref=52,kind='存疑',reason='結場界指涉待核'),
 dict(ref=62,kind='誤報',reason='處分別人譯個人法可'),
]
B.make(N, items, verdicts)
