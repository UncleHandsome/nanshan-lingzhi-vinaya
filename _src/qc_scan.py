# -*- coding: utf-8 -*-
"""零成本品管掃描：引號白話、目錄膨脹、異體字與網址殘留。

用法：
  python -X utf8 _src/qc_scan.py --materials 測試/實驗11/_材料 --finals 測試/C版11
"""
import argparse
import io
import os
import json
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BAD_VAR = {'鉢': '缽', '厨': '廚', '徧': '遍', '牀': '床', '説': '說', '衆': '眾'}
HAN = re.compile(r'[\u4e00-\u9fff]')

def load_material(key, d):
    p = os.path.join(d, key + '.md')
    if not os.path.exists(p):
        return '', []
    t = io.open(p, encoding='utf-8').read()
    srcs = re.findall(r'■ (?:疏文|記文|鈔文|律文|註文|序文)（原文）(?:\[\d+\])?\s*\n(.*?)(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求|所釋鈔文)|\Z)', t, re.S)
    return t, [s.strip() for s in srcs]


LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')
LEAD_LAB = re.compile(r'^\s*【(%s)】' % '|'.join(LABELS))


def check_lead_label(out):
    """譯文開頭必須是合法段別標籤（只認白名單六種）。"""
    return [] if LEAD_LAB.match(out or '') else ['譯文開頭缺合法段別標籤']


def check_bracket_overflow(src, out):
    """譯文自加校勘／補義：〔 數不得多於原文。"""
    if (out or '').count('〔') > (src or '').count('〔'):
        return ['譯文〔〕多於原文（疑自加校勘／補義）']
    return []


def check_tail_colon(out):
    """結尾懸空冒號：原文以「云。」收尾時不得譯成「說：」。"""
    return ['譯文結尾為冒號'] if (out or '').rstrip().endswith(('：', ':')) else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--materials', required=True)
    ap.add_argument('--finals', required=True)
    args = ap.parse_args()

    md = os.path.join(B, args.materials.replace('/', os.sep))
    fd = os.path.join(B, args.finals.replace('/', os.sep))
    keys = sorted(f[:-4] for f in os.listdir(fd)
                  if f.endswith('.txt') and not f.startswith('_'))

    rows = []
    for k in keys:
        _, srcs = load_material(k, md)
        src = ''.join(srcs)
        out = io.open(os.path.join(fd, k + '.txt'), encoding='utf-8').read()

        issues = []
        # 0) 段別標籤、自加校勘、結尾懸空冒號（2026-11-22 新增）
        issues += check_lead_label(out)
        issues += check_bracket_overflow(src, out)
        issues += check_tail_colon(out)
        _j = os.path.join(md, k + '.json')
        if os.path.exists(_j):
            try:
                _d = json.load(io.open(_j, encoding='utf-8'))
                if _d.get('packed'):
                    _need = len(_d.get('segments') or []) or len(_d.get('members') or [])
                    _nums = [int(n) for n in re.findall(r'(?m)^\s*\[\s*(\d+)\s*\]', out)]
                    if _need and sorted(set(_nums)) != list(range(1, _need + 1)):
                        issues.append('打包段編號不完整（需 1..%d，得 %s）' % (_need, sorted(set(_nums))))
            except Exception:
                pass
        # 1) 引號內半文半白（純白話引文＝體例允許；純文言引文＝先引原文體例）
        #    文言虛字只認「者也／矣／焉／哉」與句末「乎」，避免「也沒有」「幾乎」誤判
        for _q in re.findall(r'[「『]([^」』]{8,})[」』]', out):
            if (len(HAN.findall(_q)) >= 10
                    and re.search(r'[的了著嗎呢吧]', _q)
                    and re.search(r'者也|[矣焉哉]|乎[，。；：！？]', _q)):
                issues.append('引號內疑半文半白')
                break
        # 2) 短文膨脹（夾注白話計入括號，不重複計入正文倍率）
        sh = len(HAN.findall(src))
        out_plain = re.sub(r'^【(?:疏文|記文|鈔文|律文|註文|序文)】\s*', '', out)
        out_plain = re.sub(r'（[^）]*）|\([^)]*\)|〔[^〕]*〕', '', out_plain)
        oh = len(HAN.findall(out_plain))
        if sh >= 10 and oh < sh * 0.4:
            issues.append('嚴重縮水（疑漏譯）')
        if 10 <= sh <= 75 and oh > sh * 2.4:
            issues.append('短文膨脹 %d→%d 字' % (sh, oh))
        if 200 <= sh <= 440 and oh > sh * 1.85:
            issues.append('中長段膨脹 %d→%d 字' % (sh, oh))

        # 3) 殘留
        if re.search(r'〔[^〕]*(?:據|按|考|校)[^〕]*〕', out) or re.search(r'〔疑作[^〕]{1,10}(?:據|卷|頁)', out):
            issues.append('〔〕內疑含校勘按語')
        _out_pars = [x.strip() for x in re.findall(r'[（(]([^）)]*)[）)]', out)
                     if not re.fullmatch(r'[一二三四五六七八九十百千\d]+', x.strip())
                     and not re.fullmatch(r'[^，。；]{0,8}反', x.strip())]
        _src_notes = max(0, src.count('（') + src.count('(') + src.count('〔') - out.count('〔'))
        if len(_out_pars) > _src_notes:
            issues.append('疑自加解說括號（譯 %d＞原 %d）' % (len(_out_pars), _src_notes))
        if 'PASS_A_KEEP_A' in out:
            issues.append('殘留 PASS_A 標記')
        if re.search(r'(?m)^\s*(?:以下為.{0,16}整合|以下為整合|最終定稿白話版|完整修正版)', out):
            issues.append('殘留整合說明')
        if re.search(r'《(?:四分|十誦|五分|僧祇|摩訶僧祇)》', out):
            issues.append('律名簡稱未補「律」字')
        _out_norm = out.replace('毗', '毘')
        _src_norm = src.replace('毗', '毘')
        for _full in ('《薩婆多部毘尼摩得勒伽》', '《薩婆多毘尼毘婆沙》', '《律二十二明了論》',
                      '《雜阿毘曇心論》', '《優婆塞戒經》', '《成實論》', '《毘尼母經》', '《善見律毘婆沙》', '《善見律》'):
            if _full in _out_norm and re.sub(r'[《》]', '', _full) not in _src_norm:
                issues.append('簡稱疑誤展開全稱')
                break
        if re.search(r'(?m)^\s*\d+[.、]\s', out):
            issues.append('殘留數字條列')
        if re.search(r'(?:local_search|web_search|web_fetch)\s*\(', out):
            issues.append('殘留工具呼叫字面')
        for _w, _msg in (('農曆', '疑時代錯置（農曆）'),):
            if _w in out and _w not in src:
                issues.append(_msg)
        _quotes = ''.join(re.findall(r'[「『]([^」』]*)[」』]', out))
        _simp_src = re.sub(r'[「『][^」』]*[」』]', '', out)
        if any(_b in _quotes for _b in ('这', '为', '应', '经', '说', '义', '体', '归')):
            issues.append('引號內疑簡體')
        for _bad in ('达', '没', '时', '精准', '颗', '过', '与', '现', '实', '际', '种', '样', '动', '学', '觉', '见', '观', '识', '论', '证', '众', '问', '这', '为', '应', '经', '说', '义', '体', '归', '无', '过', '还', '对', '发', '个', '们', '么', '护', '卫', '断', '灭', '尽', '离', '广', '严', '华', '乐', '礼', '处', '复', '单', '双', '当', '该', '传', '记', '书', '门', '与', '从', '来', '现', '实', '际', '种', '样', '动', '学', '觉', '见', '观', '识', '论', '证'):
            if _bad in _simp_src:
                issues.append('殘留簡體字')
                break
        for _a, _b, _n in (('「', '」', '「」'), ('『', '』', '『』'),
                            ('（', '）', '（）'), ('《', '》', '《》'), ('〔', '〕', '〔〕')):
            if out.count(_a) != out.count(_b):
                issues.append(_n + ' 未成對')
        if re.search(r'[（(]\s*[）)]', out):
            issues.append('殘留空括號（）')
        if 'http' in out:
            issues.append('殘留網址')
        _out_noquote = re.sub(r'[「『][^」』]*[」』]', '', out)
        for bad, good in BAD_VAR.items():
            if bad in _out_noquote:
                issues.append('異體字 %s' % bad)
        _labs = re.findall(r'(?m)^【(疏文|記文|鈔文|律文|註文|序文)】', out)
        if any(_labs.count(x) > 1 for x in set(_labs)):
            issues.append('殘留欄位標籤')

        rows.append((k, issues))

    print('%-4s %s' % ('組', '檢查結果'))
    n_bad = 0
    for k, iss in rows:
        if iss:
            n_bad += 1
            print('%-4s ⚠ %s' % (k, '；'.join(iss)))
        else:
            print('%-4s ✅' % k)
    print('\n需人工複核：%d／%d 組' % (n_bad, len(rows)))


if __name__ == '__main__':
    main()
