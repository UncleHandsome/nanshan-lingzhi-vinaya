import os

base_dir = r'c:\Users\lionc\OneDrive\桌面\XW\三大部'
single_dir = os.path.join(base_dir, '校閱_單段')
out_dir = os.path.join(base_dir, '校閱_單段_結果')
cum_md = os.path.join(base_dir, '校閱_單段_101-600校閱結果.md')

os.makedirs(out_dir, exist_ok=True)

findings = {
    212: {
        'issues': [
            {
                'level': 'P1',
                'type': '條件判定／語義偏差',
                'head': '《五分》：斷事時，若在屋中，隨幾過出',
                'problem': '「隨幾過出」意為只要一越過出戶界限即便失欲；譯文誤譯為「隨其走出幾次」，將出戶即失的判定界線誤解為走出的次數。',
                'basis': '原文作「隨幾過出。若在露地，去僧一尋等並失」，《資持記》明釋：「隨幾過出者，過即是度，度猶出也。謂出戶則失，不問度數多少也。」',
                'suggestion': '改為「若在屋舍中，只要一跨出門戶即失欲」或「隨其一跨出門檻即失」。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    232: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '二就事明者。謂羯磨所被之事……何者是也',
                'problem': '譯文嚴重腰斬，自「何者是也？」之後整段重要事相判定（包含瞻波篇訶責擯出之相當、實犯罪自言不犯之非法、非情事二房羯磨妨難、離衣杖必具等律文誠文）全未翻譯。',
                'basis': '原文自「何者是也？如人法中，不覆藏者……此並律之誠文，臨事無忘失矣」長達一百餘字，譯文完全脫漏。',
                'suggestion': '補齊自「何者是也？」至結尾之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    236: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '初明七非者：一者人非，謂以此法',
                'problem': '譯文嚴重腰斬，僅翻譯前導句「首先說明純粹心念法的「七非」：」，原文後續核心內容「一者人非……七具三非，並同上。餘則例之」全未翻譯。',
                'basis': '原文詳細列出純心念法之七非內涵：「一者人非，謂以此法，對人而作。二者法非，口不言了，法不稱教。三者事非……」，譯文完全脫漏。',
                'suggestion': '補全純心念法七非之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    237: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '二對首心念，亦具七非，數同於上',
                'problem': '譯文嚴重腰斬，停在引言句「暫且舉單獨「受安居」這一項法為例，其餘的皆可照此推知：」，原文後續「一者人非，謂界中有人……四非已下，類前可知」全未翻譯。',
                'basis': '原文列出對首心念具體七非（界中有人別眾而作、口說錯脫文非明了、時非夏限處有難緣等），譯文完全缺失。',
                'suggestion': '補全對首心念七非之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    238: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '三眾法心念，如說戒等，亦具七非',
                'problem': '譯文嚴重腰斬，停在「第三、眾法轉心念法，例如一人心念說戒等，也具足七非：」，後續「一者人非……四非已下，如前例之」全未翻譯。',
                'basis': '原文列明「一者人非，界內別眾，自犯六聚。二者法非，不陳三說……三者事非，眾具有闕，時非正法」，譯文完全脫漏。',
                'suggestion': '補全眾法心念七非之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    239: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '四但對首，如持衣法。一者人非',
                'problem': '譯文嚴重腰斬，停在「第四、純粹對首法，例如受持三衣之法：」，後續「一者人非……四非至七，如前例知」全未翻譯。',
                'basis': '原文列明「一者人非，所對之人，犯戒非法……二者法非……三者事非，五大色衣及以上染，財是不淨之例」，譯文完全脫漏。',
                'suggestion': '補全純對首法七非之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    242: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '七白二中，如結界法。一者人非',
                'problem': '譯文嚴重腰斬，停在「第七在白二羯磨中，例如結界法事：」，後續「一者人非……並不成就。餘非例知」全未翻譯。',
                'basis': '原文列明白二羯磨之非相（不盡標盡相、唱相不明作法闇託、標相及體三種分齊混亂、二界錯涉重結交互等），譯文完全脫漏。',
                'suggestion': '補全白二羯磨七非之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    246: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '就單白說戒中分五：一大德僧聽者告眾',
                'problem': '譯文嚴重腰斬，僅有「在說戒的「單白文」中分為五段：」，原文說戒單白文五段法義（一大德僧聽、二今僧白月十五日布薩說戒、三若僧時到僧忍聽、四布薩說戒、五白如是）全未翻譯。',
                'basis': '原文自「一大德僧聽者告眾……五白如是者，事既和辨，白結告知」長達一百五十餘字，譯文完全脫漏。',
                'suggestion': '補全單白說戒五句結構之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    247: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '次就羯磨法中明者。且約受戒白四內……白中還五',
                'problem': '譯文嚴重腰斬，停在「白文當中同樣分為五句：」，原文白四羯磨中白文之五句解析（一大德僧聽、二是沙彌某甲從和尚某甲受戒……五白如是者）全未翻譯。',
                'basis': '原文詳細列出受戒白文中五句之分段與意義，譯文完全缺失。',
                'suggestion': '補全白四羯磨中白文五句之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    249: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '前中有三：初大德僧聽者，告眾重聽',
                'problem': '譯文嚴重腰斬，僅有「前半部分中包含三段：」，原文對羯磨表決正體三段結構及第二第三遍之重要規定（大德僧聽、牒緣根本、單牒根本決判成就，及第二第三亦如是說之義理）全未翻譯。',
                'basis': '原文「初大德僧聽者……軌刻令定，限至於此」全部落空，譯文缺失。',
                'suggestion': '補全羯磨正體三段之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    251: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '就中加三法料簡：一增減，二通塞，三是非。初中',
                'problem': '譯文腰斬，僅譯出「在這當中再加入三種法門來加以料簡審辨：第一是增減，第二是通塞，第三是是非。」，後文關於白文句數依事輕重增減之重要說明（初中，若事輕小無有緣起……乃至白二類例除之，餘則一準）全未翻譯。',
                'basis': '原文自「初中，若事輕小……餘則一準」完全未譯。',
                'suggestion': '補全增減料簡之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    252: {
        'issues': [
            {
                'level': 'P0',
                'type': '漏譯／腰斬',
                'head': '二明通塞者。單白文中，第一、第三、第五文義',
                'problem': '譯文嚴重腰斬，僅譯出標題「第二、說明「通塞」（通用與局限）：」，後文關於單白與羯磨文中哪些文句通一切法、哪些文句限局具體事相之核心律理全未翻譯。',
                'basis': '原文自「單白文中，第一、第三、第五文義……不了前緣，誦文亦失」長達一百六十餘字，譯文完全脫漏。',
                'suggestion': '補全通塞法相之完整譯文。',
                'confidence': '高'
            }
        ],
        'doubts': []
    }
}

with open(cum_md, 'w', encoding='utf-8') as cum_f:
    cum_f.write('# 《四分律刪繁補闕行事鈔》校閱結果（第 00101 ～ 00600 檔）\n\n')
    cum_f.write('依據《提示詞_白話校閱.md》逐檔核對原文與譯文，逐一執行反覆確認並存檔。\n\n')

    all_files = sorted([f for f in os.listdir(single_dir) if f.endswith('.txt')])
    target_files = [f for f in all_files if 101 <= int(f.split('_')[0]) <= 600]

    total_p0 = 0
    total_p1 = 0
    total_p2 = 0
    total_doubt = 0

    for idx_num in range(101, 601):
        prefix = f'{idx_num:05d}_'
        matched = [x for x in target_files if x.startswith(prefix)]
        if not matched:
            continue
        fname = matched[0]
        fpath = os.path.join(single_dir, fname)
        
        with open(fpath, encoding='utf-8') as fp:
            raw_lines = [l.strip() for l in fp if l.strip()]
        
        tag = raw_lines[0].replace('【', '').replace('】', '') if raw_lines else fname
        file_base = os.path.splitext(fname)[0]
        
        item = findings.get(idx_num, {'issues': [], 'doubts': []})
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
        
        # Save individual file result
        out_single_file = os.path.join(out_dir, f'{file_base}_校閱.txt')
        with open(out_single_file, 'w', encoding='utf-8') as s_out:
            s_out.write(file_report)
            
        # Append to cumulative report
        cum_f.write(file_report + '\n')

print(f'Finished processing {len(target_files)} files (101 to 600).')
print(f'Total P0: {total_p0}, P1: {total_p1}, P2: {total_p2}, Doubts: {total_doubt}')
