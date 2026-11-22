# -*- coding: utf-8 -*-
"""義鈔短段句讀套用（只改 display_source，source 不動）。

做的事：
  1. 修回 display_source 尾端被截掉的句末標點（來源：重作材料_長段/句讀待補_全部_回.md，
     必須是「回覆以 display 為前綴、剩下只有標點」才算命中）。
  2. 對 30 字以上、完全無句讀的段，用 AI語譯/_work/yichao_punct.json 的精確漢字候選補句讀。
  3. row.display_source 同步為 segment.display_source。
  4. 把有句讀的 display_source 依漢字精確定位，補進
     TXT_分卷/05_拾毗尼義鈔_標點對齊 仍是無句讀的原文區間。

全程漢字序列必須完全相等；重複或定位不唯一就跳過，不做模糊比對。

用法：
  python -X utf8 _src/apply_yichao_short_punct.py            # 只檢查
  python -X utf8 _src/apply_yichao_short_punct.py --apply    # 寫入（先備份）
"""
import argparse
import io
import json
import os
import re
import shutil
import time

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
H = re.compile(r'[\u4e00-\u9fff]')
P = re.compile(r'[，。；：！？、]')
HIP = re.compile(r'[，。；：！？、）」』】》〉）\]\)]+')
WS = re.compile(r'[\s\u3000\u00a0]+')
JSONL = os.path.join(B, '定稿', 'yichao.jsonl')
REPLY_MAT = os.path.join(B, '重作材料_長段', '句讀待補_全部.md')
REPLY_OUT = os.path.join(B, '重作材料_長段', '句讀待補_全部_回.md')
YC_JSON = os.path.join(B, 'AI語譯', '_work', 'yichao_punct.json')
ALIGN = os.path.join(B, 'TXT_分卷', '05_拾毗尼義鈔_標點對齊')


def han(s):
    return ''.join(H.findall(s or ''))


def clean(s):
    return WS.sub('', s or '')


def parse_material(path):
    t = io.open(path, encoding='utf-8').read()
    out = []
    for m in re.finditer(r'^##\s+(P\d+)\s*\n(.*?)(?=^##\s+P|\Z)', t, re.M | re.S):
        body = m.group(2)
        book = re.search(r'-\s*書[：:]\s*(\S+)', body)
        lines = [ln.strip() for ln in body.split('\n')]
        text = '\n'.join(ln for ln in lines if ln and not ln.startswith('- '))
        out.append((m.group(1), book.group(1) if book else '?', text))
    return out


def parse_reply(path):
    t = io.open(path, encoding='utf-8').read()
    return {m.group(1): '\n'.join(ln.strip() for ln in m.group(2).split('\n') if ln.strip())
            for m in re.finditer(r'^##\s+(P\d+)\s*\n(.*?)(?=^##\s+P|\Z)', t, re.M | re.S)}


def build_reply_map():
    mat = parse_material(REPLY_MAT)
    rep = parse_reply(REPLY_OUT)
    out = {}
    for pid, book, text in mat:
        if book != '義鈔' or pid not in rep:
            continue
        cand = rep[pid]
        if han(cand) == han(text) and P.search(cand):
            out.setdefault(han(text), []).append(cand)
    return out


def build_yc_corpus():
    d = json.load(io.open(YC_JSON, encoding='utf-8'))
    text = clean('\n'.join(x for x in d if isinstance(x, str)))
    hb, pos = [], []
    for i, ch in enumerate(text):
        if '\u4e00' <= ch <= '\u9fff':
            hb.append(ch)
            pos.append(i)
    return ''.join(hb), text, pos


def source_tail(src):
    ms = list(H.finditer(src or ''))
    if not ms:
        return ''
    tail = (src or '')[ms[-1].end():]
    return tail if tail and HIP.fullmatch(tail) else ''


def repair_displays(rows, reply, yc):
    stats = dict(tail_repair=0, yc_fill=0, source_tail=0, unchanged=0)
    detail = []
    for r in rows:
        for si, s in enumerate(r.get('segments') or []):
            src = s.get('source') or ''
            disp = s.get('display_source') or ''
            h = han(src)
            # 1) 尾端標點被截：回覆必須以 disp 為前綴，剩下的只有標點
            fixed = None
            for cand in reply.get(h, []):
                if cand.startswith(disp) and HIP.fullmatch(cand[len(disp):] or ''):
                    fixed = cand
                    break
            if fixed and fixed != disp:
                s['display_source'] = fixed
                stats['tail_repair'] += 1
                detail.append(('tail', r['key'], disp[-12:], fixed[-12:]))
                disp = fixed
            # 2) 完全無句讀：用既有句讀語料的精確候選
            if not P.search(disp) and len(h) > 30:
                hb, text, pos = yc
                i = hb.find(h)
                if i >= 0 and hb.find(h, i + 1) < 0:
                    cand = text[pos[i]:pos[i + len(h) - 1] + 1]
                    tail = source_tail(src)
                    cand2 = cand + tail
                    if P.search(cand2) and han(cand2) == h:
                        s['display_source'] = cand2
                        stats['yc_fill'] += 1
                        detail.append(('ycfill', r['key'], '', cand2[-16:]))
                        disp = cand2
            # 3) display 是 source 的前綴，尾端只差標點（例如漏了「）」）
            sclean = WS.sub('', src)
            dclean = WS.sub('', disp)
            if sclean.startswith(dclean):
                tail = sclean[len(dclean):]
                if tail and HIP.fullmatch(tail):
                    s['display_source'] = disp + tail
                    stats['source_tail'] += 1
                    detail.append(('src', r['key'], disp[-12:], (disp + tail)[-12:]))
                    disp = disp + tail
            if not P.search(disp):
                stats['unchanged'] += 1
        if r.get('segments'):
            r['display_source'] = r['segments'][0].get('display_source') or ''
    return stats, detail


def align_replacements(rows):
    """回傳 {檔名: [(start, end, old, new, key)]}；只收無句讀且全域唯一的片段。"""
    plans = {}
    amb = []
    dup = set()
    for r in rows:
        for si, s in enumerate(r.get('segments') or []):
            h = han(s.get('source'))
            disp = s.get('display_source') or ''
            if len(h) < 30 or not P.search(disp):
                continue
            if h in dup:
                continue
            dup.add(h)
            hits = []
            for fn in sorted(os.listdir(ALIGN)):
                if not fn.endswith('.txt'):
                    continue
                t = io.open(os.path.join(ALIGN, fn), encoding='utf-8').read()
                hp = [i for i, ch in enumerate(t) if '\u4e00' <= ch <= '\u9fff']
                hs = ''.join(t[i] for i in hp)
                k = hs.find(h)
                while k >= 0:
                    hits.append((fn, t, hp, k))
                    k = hs.find(h, k + 1)
            if len(hits) != 1:
                if len(hits) > 1:
                    amb.append((r['key'], len(h), 'multi', len(hits)))
                continue
            fn, t, hp, k = hits[0]
            a = hp[k]
            b = hp[k + len(h) - 1] + 1
            raw = t[a:b]
            if P.search(raw) or han(raw) != h:
                continue
            m = HIP.match(t, b)
            e = m.end() if m else b
            plans.setdefault(fn, []).append((a, e, t[a:e], disp, r['key']))
    # 去掉重疊：大的優先，重疊者跳過
    for fn, lst in plans.items():
        lst.sort(key=lambda x: (x[0], -(x[1] - x[0])))
        kept = []
        for x in lst:
            if any(not (x[1] <= y[0] or x[0] >= y[1]) for y in kept):
                amb.append((x[4], x[1] - x[0], 'overlap', ''))
                continue
            kept.append(x)
        plans[fn] = kept
    return plans, amb


def write_align(plans):
    touched = {}
    for fn, lst in plans.items():
        p = os.path.join(ALIGN, fn)
        old_bytes = io.open(p, 'rb').read()
        nl = '\r\n' if b'\r\n' in old_bytes else '\n'
        t = old_bytes.decode('utf-8').replace('\r\n', '\n')
        old_han = han(t)
        for a, e, old, new, key in sorted(lst, key=lambda x: -x[0]):
            if t[a:e] != old:
                raise RuntimeError('定位內容已變：%s %s' % (fn, key))
            t = t[:a] + new + t[e:]
        if han(t) != old_han:
            raise RuntimeError('漢字序列改變：%s' % fn)
        io.open(p, 'w', encoding='utf-8', newline=nl).write(t)
        touched[fn] = len(lst)
    return touched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    rows = [json.loads(x) for x in io.open(JSONL, encoding='utf-8') if x.strip()]
    src_before = {r['key']: r.get('source') for r in rows}
    reply = build_reply_map()
    yc = build_yc_corpus()
    print('回覆候選段（漢字唯一）', len(reply), '；句讀語料字數', len(yc[0]))

    stats, detail = repair_displays(rows, reply, yc)
    print('display 修復：', stats)
    for d in detail[:8]:
        print('  ', d)
    src_after = {r['key']: r.get('source') for r in rows}
    assert src_before == src_after, 'source 被改動'

    plans, amb = align_replacements(rows)
    total = sum(len(v) for v in plans.values())
    print('標點對齊可補：', total, {k: len(v) for k, v in plans.items()})
    if amb:
        print('跳過（重複／重疊／多位置）：', len(amb))
        for x in amb[:15]:
            print('  ', x)

    # 統計
    no_punct = [r for r in rows if not P.search(r['segments'][0].get('display_source') or '')]
    short = [r for r in rows if 100 <= len(han(r['segments'][0].get('source'))) <= 500]
    short_ok = [r for r in short if P.search(r['segments'][0].get('display_source') or '')]
    print('100–500 段', len(short), '有句讀', len(short_ok))
    print('仍完全無句讀', len(no_punct), '最長',
          max((len(han(r['segments'][0].get('source'))) for r in no_punct), default=0))

    if not args.apply:
        print('（檢查模式，未寫入）')
        return

    stamp = time.strftime('%Y%m%d_%H%M%S')
    bk_jsonl = os.path.join(B, '定稿', '_舊_yichao_before_shortpunct_%s.jsonl' % stamp)
    shutil.copy2(JSONL, bk_jsonl)
    nl = '\r\n' if b'\r\n' in io.open(JSONL, 'rb').read() else '\n'
    tmp = JSONL + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + nl)
    os.replace(tmp, JSONL)
    print('已寫定稿：', JSONL, '備份：', bk_jsonl)

    bkdir = os.path.join(B, 'TXT_分卷', '_備份_05_拾毗尼義鈔_標點對齊_' + stamp)
    os.makedirs(bkdir, exist_ok=True)
    for fn in sorted(os.listdir(ALIGN)):
        if fn.endswith('.txt'):
            shutil.copy2(os.path.join(ALIGN, fn), os.path.join(bkdir, fn))
    touched = write_align(plans)
    print('已寫標點對齊：', touched, '備份：', bkdir)

    with io.open(os.path.join(B, '重作材料_長段', '_義鈔短段句讀_stats.json'),
                 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(stats=stats, align=touched, short=len(short),
                       short_ok=len(short_ok), no_punct=len(no_punct),
                       backup_jsonl=bk_jsonl, backup_align=bkdir),
                  f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
