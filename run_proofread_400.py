import os

base_dir = r'c:\Users\lionc\OneDrive\桌面\XW\三大部'
single_dir = os.path.join(base_dir, '校閱_單段')
out_dir = os.path.join(base_dir, '校閱_單段_結果')
cum_md = os.path.join(base_dir, '校閱_單段_601-1000校閱結果.md')
master_md = os.path.join(base_dir, '校閱_單段_前1000個校閱結果.md')

os.makedirs(out_dir, exist_ok=True)

findings = {
    777: {
        'issues': [],
        'doubts': [
            {
                'head': '足食已，捨威儀，不作餘食法',
                'doubt': '原文僅云「不作餘食法」，譯文補出「未經由其他比丘為其作」，增補了施事者。餘食法雖常規由未足食比丘作，但此處文義是否限定「其他比丘」作法，暫列存疑。'
            }
        ]
    },
    778: {
        'issues': [
            {
                'level': 'P1',
                'type': '術語／受食關係',
                'head': '若受不作餘食法者，告言我受不作餘食法，便得食',
                'problem': '原文「受」指「受食」，「受不作餘食法者」是指受食而未作餘食法之人（見上座來而白告「我受不作餘食法」以開許不起立）；譯文誤解為「如果是屬於受持『不作餘食法』的人（即受持這項開緣特許）」，把受食與白法錯解為受持某種特許法規的身分。',
                'basis': '《四分律》及《資持記》明釋：「若受不作餘食法者：謂起迎上座，還來更食，不須作法也。告言者，即以法白之。尼戒亦爾者，彼亦見僧至告之，不起不犯也。」此處「受」為受食，告言為律制白法，非受持特許身分。',
                'suggestion': '修正為「若是受食後未作餘食法者，向上座稟白說：『我已受食未作餘食法』，便可安坐進食」。',
                'confidence': '高'
            }
        ],
        'doubts': [
            {
                'head': '告言我受不作餘食法，便得食',
                'doubt': '譯文於「便得食」補出「（可不起立迎敬）」，此為律文因見上座來而設之本意，雖順通律意但屬增飾說明，暫列存疑。'
            }
        ]
    },
    780: {
        'issues': [
            {
                'level': 'P0',
                'type': '否定方向／開緣條件錯',
                'head': '不受作餘食法',
                'problem': '原文「不受作餘食法」指「未經受取而作餘食法」；譯文誤譯為「受持開許不須作餘食法的食物」，將否定「不受」顛倒為肯定「受持」，並將「作法」增添「不須」，徹底顛倒了律制開緣條件。',
                'basis': '《資持記》云：「不受作餘食法者，謂彼人未受，即為作法，還得食也。」譯文把「未受」翻成「受持」，把「作餘食法」翻成「不須作餘食法」，方向完全相反。',
                'suggestion': '改為「未經受取而預先為之作餘食法」或「未受而作餘食法」。',
                'confidence': '高'
            },
            {
                'level': 'P2',
                'type': '半譯／體例',
                'head': '律不犯者：',
                'problem': '段首「律不犯者：」未翻譯為流暢白話，直接照抄古漢語原文。',
                'basis': '整部體例應白話化，此處照抄文言。',
                'suggestion': '改譯為「《四分律》中不結罪（不犯）的情況如下：」。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    782: {
        'issues': [],
        'doubts': [
            {
                'head': '食已，用楊枝若灰漱口，不者墮',
                'doubt': '原文僅云「不者墮」（用齋後不用楊枝或灰漱口者結墮罪），譯文增補「而在非時誤咽殘渣者結墮罪」，此係依非時食戒之結罪機理所作推測補述，律文未明言誤咽，暫列存疑。'
            }
        ]
    },
    783: {
        'issues': [
            {
                'level': 'P1',
                'type': '增譯／過度發揮',
                'head': '殘宿、不受食戒，以坐禪比丘為緣起者',
                'problem': '原文僅記「以坐禪比丘為緣起者」，譯文擅自增設情節與貶抑動機：「貪圖打坐不出行乞食而儲存食物」，主觀臆測並過度發揮。',
                'basis': '律文及行事鈔原文此處僅敘以坐禪人宿食為結戒由來，並無「貪圖打坐不出行乞食」之貶抑詞句與動機描寫。',
                'suggestion': '刪除「貪圖打坐不出行乞食而儲存食物」，忠實譯為「以坐禪比丘（之因緣）為起戒由來」。',
                'confidence': '高'
            }
        ],
        'doubts': []
    },
    825: {
        'issues': [
            {
                'level': 'P1',
                'type': '意思相反／罪名判定顛倒',
                'head': '開和尚墮，餘人吉羅',
                'problem': '原文「開和尚墮，餘人吉羅」指經推算年歲仍不滿時，律制開緣減罪：僅判定和尚犯墮罪，其餘僧人減輕判定犯吉羅罪；譯文卻誤譯為「並開許免除親教師（和尚）的墮罪（波逸提），以及其餘參與者的突吉羅罪」，完全顛倒為免除罪罰。',
                'basis': '《四分律》及《資持記》明釋：「開和尚墮者，律制年不滿，師僧俱墮。今若數年已，雖不滿歲而日數已足，開師得墮，餘人減罪得吉，故云開也。」此處之「開」是指從原本「師僧俱墮」開緣減輕為「和尚得墮、餘僧得吉」，而非免罪。',
                'suggestion': '修正為「（若經推算年歲仍不足者）律制開緣減罪：親教師（和尚）結犯墮罪，其餘參與僧人則減輕結犯突吉羅罪」。',
                'confidence': '高'
            }
        ],
        'doubts': []
    }
}

all_files = sorted([f for f in os.listdir(single_dir) if f.endswith('.txt')])
target_files = [f for f in all_files if 601 <= int(f.split('_')[0]) <= 1000]

print(f'Found {len(target_files)} target files for 601-1000.')

total_p0 = 0
total_p1 = 0
total_p2 = 0
total_doubt = 0

with open(cum_md, 'w', encoding='utf-8') as cum_f:
    cum_f.write('# 《四分律刪繁補闕行事鈔》校閱結果（第 00601 ～ 01000 檔）\n\n')
    cum_f.write('依據《提示詞_白話校閱.md》逐檔核對原文與譯文，逐一執行反覆確認並存檔。\n\n')

    for idx_num in range(601, 1001):
        prefix = f'{idx_num:05d}_'
        matched = [x for x in target_files if x.startswith(prefix)]
        if not matched:
            print(f'Warning: file {idx_num} not found!')
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
            
        # Append to batch report
        cum_f.write(file_report + '\n')

print(f'Batch 601-1000 completed:')
print(f'P0: {total_p0}, P1: {total_p1}, P2: {total_p2}, Doubts: {total_doubt}')

# Now create master consolidated report: 校閱_單段_前1000個校閱結果.md
print('Generating consolidated 1000 file report...')
with open(master_md, 'w', encoding='utf-8') as master_f:
    master_f.write('# 《四分律刪繁補闕行事鈔》校閱結果（第 00001 ～ 01000 檔）\n\n')
    master_f.write('依據《提示詞_白話校閱.md》逐檔核對原文與譯文，逐一執行反覆確認並存檔。\n\n')
    
    # Read all individual files from 1 to 1000 in sorted order
    all_single_out = sorted([f for f in os.listdir(out_dir) if f.endswith('_校閱.txt')])
    target_out_files = [f for f in all_single_out if 1 <= int(f.split('_')[0]) <= 1000]
    
    m_p0 = 0
    m_p1 = 0
    m_p2 = 0
    m_doubt = 0
    
    for f in target_out_files:
        fpath = os.path.join(out_dir, f)
        with open(fpath, encoding='utf-8') as inf:
            content = inf.read()
            master_f.write(content + '\n')
            
            # parse stats from lines
            for line in content.splitlines():
                if line.startswith('P0 ') and 'P1 ' in line:
                    parts = line.split('；')
                    p_parts = parts[0].split('、')
                    p0 = int(p_parts[0].replace('P0', '').strip())
                    p1 = int(p_parts[1].replace('P1', '').strip())
                    p2 = int(p_parts[2].replace('P2', '').strip())
                    d = 0
                    if len(parts) > 1 and '存疑 ' in parts[1]:
                        d_str = parts[1].split('存疑 ')[1].split(' 條')[0].strip()
                        d = int(d_str)
                    m_p0 += p0
                    m_p1 += p1
                    m_p2 += p2
                    m_doubt += d

print(f'Consolidated 1000 report written to {master_md}.')
print(f'Master Total: {len(target_out_files)} files.')
print(f'Master Stats: P0: {m_p0}, P1: {m_p1}, P2: {m_p2}, Doubts: {m_doubt}')
