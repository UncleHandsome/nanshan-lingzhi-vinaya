import os

base_dir = r'c:\Users\lionc\OneDrive\桌面\XW\三大部'
single_dir = os.path.join(base_dir, '校閱_單段')
out_dir = os.path.join(base_dir, '校閱_單段_結果')
cum_md = os.path.join(base_dir, '校閱_單段_前100個校閱結果.md')

os.makedirs(out_dir, exist_ok=True)

findings = {
    6: {
        'issues': [
            {
                'level': 'P1',
                'type': '因果／語義邏輯',
                'head': '致令辨析釁戾，輕重倍分；眾網維持，同異區別。',
                'problem': '「眾網維持，同異區別」承接「致令」，是敘述前修之弊導致僧網混亂、各執同異；譯文譯作「僧團的綱維要維持，同異之間必須加以區別」，將弊端後果誤譯為正向主動的應辦事項。',
                'basis': '原文作「致令辨析釁戾，輕重倍分；眾網維持，同異區別」，兩句皆承「致令」而來，明事乖統攝，非倡導之語。',
                'suggestion': '改為「致使辨析時產生矛盾乖戾，輕重的判定加倍分歧；僧綱的維持各生異見，同異之間互相強分。」',
                'confidence': '高'
            },
            {
                'level': 'P1',
                'type': '術語／語義偏差',
                'head': '自非統教意之廢興……孰能闢重疑，遣通累',
                'problem': '「遣通累」中的「通」為通途、共通之義，通累即普遍妨道之障累；譯文作「通達的滯累」，語意自相矛盾。',
                'basis': '原文作「遣通累」，《資持記》釋：「通，猶常也。累，即妨道之累。」',
                'suggestion': '改為「排遣通途的障累」或「遣除普遍的滯累」。',
                'confidence': '高'
            }
        ],
        'doubts': [
            {
                'head': '自非統教意之廢興……孰能闢重疑',
                'doubt': '「闢重疑」譯作「開闢重大的疑義」，現代語感易解為引發疑端；但《資持記》釋「闢，開也。重疑，即不了之義」，古訓開闢含開啟剖析之意，有底本訓詁依據，故列入存疑而不列確定錯誤。'
            }
        ]
    },
    8: {
        'issues': [
            {
                'level': 'P1',
                'type': '範圍縮小／字義誤解',
                'head': '余因聽采之暇，顧眄群篇；通非屬意',
                'problem': '「通非屬意」之「通」為副詞，意為全然、統統，「通非屬意」指群篇全都不合心意；譯文誤將「通」當名詞，譯為「對那些不通達的地方並不稱意」，將對整體的評判縮小為局部。',
                'basis': '原文「顧眄群篇；通非屬意」，《資持記》明確解為：「通非屬意者，謂都不稱心也。」',
                'suggestion': '改為「全都不合心意」或「總不稱心」。',
                'confidence': '高'
            },
            {
                'level': 'P1',
                'type': '術語／語意偏差',
                'head': '長見必錄，以輔博知；濫述必剪',
                'problem': '「長見」是指各家有所取之長處、卓見，與後文「濫述」相對；譯文作「長遠見解」，偏離本義。',
                'basis': '原文作「長見必錄」，《資持記》釋：「長見，謂有所長也。」',
                'suggestion': '改為「凡有所長之見必定記錄」或「有可取長處之見解必定錄取」。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    54: {
        'issues': [
            {
                'level': 'P1',
                'type': '術語錯',
                'head': '統明律藏，本實一文……競采大眾之文',
                'problem': '「競采大眾之文」的「大眾」指迦葉尊者窟內大會全體結集之根本律藏；譯文誤譯為部派名「大眾部」，導致各部派皆採集大眾部文句的錯誤教史結論。',
                'basis': '原文作「競采大眾之文，用集一家之典」，《資持記》明釋：「競采大眾者，如上迦葉大會，同聞佛敕，所演律藏，總號大眾。下云一家之典，即部執自分也。」',
                'suggestion': '將「競相採集大眾部的文句」修正為「競相採擷結集大眾所傳之律文」或「競相採集大會大眾之文」。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    57: {
        'issues': [],
        'doubts': [
            {
                'head': '餘有律文不了，事在廢前',
                'doubt': '「事在廢前」《資持記》解為「文隱義晦，臨事不彰，同於廢也」，意指因律文不明導致行事瀕於廢絕。譯文作「事情卻在廢除之前的」，字面直譯略顯晦澀，但未直接構成反義或硬傷，列入存疑。'
            }
        ]
    }
}

with open(cum_md, 'w', encoding='utf-8') as cum_f:
    cum_f.write('# 《四分律刪繁補闕行事鈔》校閱結果（第 00001 ～ 00100 檔）\n\n')
    cum_f.write('依據《提示詞_白話校閱.md》逐檔核對原文與譯文，逐一執行反覆確認並存檔。\n\n')

    all_files = sorted([f for f in os.listdir(single_dir) if f.endswith('.txt')])[:100]
    total_p0 = 0
    total_p1 = 0
    total_p2 = 0
    total_doubt = 0

    for idx, fname in enumerate(all_files, 1):
        fpath = os.path.join(single_dir, fname)
        with open(fpath, encoding='utf-8') as fp:
            raw_lines = [l.strip() for l in fp if l.strip()]
        
        tag = raw_lines[0].replace('【', '').replace('】', '') if raw_lines else fname
        file_base = os.path.splitext(fname)[0]
        
        item = findings.get(idx, {'issues': [], 'doubts': []})
        issues = item['issues']
        doubts = item['doubts']
        
        p0_cnt = sum(1 for x in issues if x['level'] == 'P0')
        p1_cnt = sum(1 for x in issues if x['level'] == 'P1')
        p2_cnt = sum(1 for x in issues if x['level'] == 'P2')
        d_cnt = len(doubts)
        
        total_p0 += p0_cnt
        total_p1 += p1_cnt
        total_p2 += p2_cnt
        total_doubt += d_cnt
        
        buf = []
        buf.append(f'## {file_base}\n')
        
        for iss in issues:
            lvl = iss['level']
            tp = iss['type']
            buf.append(f'### {tag}｜{lvl}｜{tp}')
            buf.append(f"- 原文起首：{iss['head']}")
            buf.append(f"- 問題：{iss['problem']}")
            buf.append(f"- 依據：{iss['basis']}")
            buf.append(f"- 建議：{iss['suggestion']}")
            buf.append(f"- 信心：{iss['confidence']}\n")
            
        for d in doubts:
            buf.append(f'### 存疑｜{tag}')
            buf.append(f"- 原文起首：{d['head']}")
            buf.append(f"- 存疑：{d['doubt']}\n")
            
        doubt_str = f'；存疑 {d_cnt} 條（{tag}）' if d_cnt > 0 else '；存疑 0 條'
        buf.append('=== 本檔結束 ===')
        buf.append(f'檔案編號：{tag}')
        buf.append('已檢查 1／1 段')
        buf.append(f'P0 {p0_cnt}、P1 {p1_cnt}、P2 {p2_cnt}{doubt_str}\n')
        
        file_report = '\n'.join(buf)
        
        out_single_file = os.path.join(out_dir, f'{file_base}_校閱.txt')
        with open(out_single_file, 'w', encoding='utf-8') as s_out:
            s_out.write(file_report)
            
        cum_f.write(file_report + '\n')

print(f'Finished processing {len(all_files)} files.')
print(f'Total P0: {total_p0}, P1: {total_p1}, P2: {total_p2}, Doubts: {total_doubt}')
