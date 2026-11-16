# -*- coding: utf-8 -*-
"""裁決前打包：同卷相鄰短段併成一份裁決材料（≤6 段、原文字合計 ≤300）。

用法：
  python -X utf8 _src/pack_judge.py --materials 重譯/業疏/_裁決材料 --out 重譯/業疏/_裁決_pack --mode pack
  python -X utf8 _src/pack_judge.py --out ... --mode split --replies 回覆 --mat 重譯/業疏/_裁決材料
"""
import argparse
import io
import json
import os
import re
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import materials_io as MI  # noqa: E402

MAX_GROUPS = 6
MAX_CHARS = 300
LABS = '疏文|記文|鈔文|律文|註文|序文'
LBL_RE = re.compile(r'■ (' + LABS + r')（(原文|譯本甲|譯本乙)）(?:\[\d+\])?\s*\n+(.+?)(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求)|\Z)', re.S)

RULE = ('【分段要求】本單元含 {n} 個獨立短段，請依下列規則處理：\n'
        '1. 僅當第 1～{n} 段「全部」無實質分歧與硬傷時，才判 `PASS_A`，第 3 欄只寫 `PASS_A_KEEP_A`。\n'
        '2. 只要任一段須改，即判 `REVISED`；第 3 欄只需列出「有改動」的段，於各標籤下按 `[n]` 書寫；'
        '未列出的段將自動沿用譯本甲，無須抄寫，亦不得寫 `PASS_A_KEEP_A`。\n'
        '3. 第 2 欄請在每條前加註段號，例如 `[1][疏] 原文「……」｜……`。\n'
        '4. 正文內子條目序數用一、二、（一）（二），嚴禁額外使用 `[數字]` 或 `-`／`*`／`1.` 項目符號。')

def blocks(text):
    d = {}
    for lab, kind, body in LBL_RE.findall(text):
        d.setdefault(lab, {})[kind] = body.strip()
    return d


def norm_len(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s))


def _emit_single(mat, out, key):
    for ext in ('.md', '.json'):
        s = os.path.join(mat, key + ext)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(out, key + ext))


def do_pack(mat, out):
    os.makedirs(out, exist_ok=True)
    for _f in os.listdir(out):
        if _f.endswith(('.md', '.json')):
            os.remove(os.path.join(out, _f))
    items = []
    for f in sorted(os.listdir(mat)):
        if not f.endswith('.md'):
            continue
        t = io.open(os.path.join(mat, f), encoding='utf-8').read()
        md = MI.load(mat, f[:-3]) or {}
        m = re.search(r'（出處：([^，]+)', t)
        ch = md.get('chunk') or (m.group(1) if m else f[:-3].rsplit('_', 1)[0])
        bl = blocks(t)
        total = sum(norm_len(v.get('原文', '')) for v in bl.values())
        items.append(dict(key=f[:-3], chunk=ch, md=md, text=t, bl=bl, n=total,
                          packed=bool(md.get('packed'))))

    def _sk(it):
        _s = it['md'].get('s0')
        if _s is None:
            _m = re.search(r'(\d+)$', it['key'])
            _s = int(_m.group(1)) if _m else 0
        return (str(it['md'].get('chunk') or it['chunk']), int(_s))
    items.sort(key=_sk)
    packs = []
    cur = []
    for it in items:
        if it['packed']:
            if cur:
                packs.append(cur)
                cur = []
            packs.append([it])
            continue
        _prev = cur[-1]['md'] if cur else {}
        _cont = (not cur) or (_prev.get('g1') is not None and it['md'].get('s0') is not None
                             and int(_prev.get('g1')) == int(it['md'].get('s0')))
        _na = re.search(r'(\d+)$', it['key'])
        _nb = re.search(r'(\d+)$', cur[-1]['key']) if cur else None
        _gap = bool(cur and not _cont and _na and _nb and int(_na.group(1)) - int(_nb.group(1)) != 1)
        if cur and (_gap
                    or sorted(it['bl']) != sorted(cur[0]['bl'])
                    or it['chunk'] != cur[0]['chunk'] or len(cur) >= MAX_GROUPS
                    or sum(x['n'] for x in cur) + it['n'] > MAX_CHARS):
            packs.append(cur)
            cur = []
        cur.append(it)
    if cur:
        packs.append(cur)

    index = {}
    n = 0
    for pack in packs:
        if len(pack) < 2:
            _emit_single(mat, out, pack[0]['key'])
            n += 1
            continue
        key = 'p%04d' % (len(index) + 1)
        head = pack[0]['text'].split('【本次待審單元】')[0].rstrip()
        labs = []
        for it in pack:
            for lab in it['bl']:
                if lab not in labs:
                    labs.append(lab)
        lines = [head, '', '【本次待審單元】', '', RULE.format(n=len(pack)), '',
                 '【輸出標籤】' + '／'.join('【%s】' % x for x in labs) + '（標籤寫在該欄最前一次，'
                 '其下逐條列 [n]）', '']
        for i, it in enumerate(pack, 1):
            for lab, v in it['bl'].items():
                for kind in ('原文', '譯本甲', '譯本乙'):
                    if v.get(kind):
                        lines += ['■ %s（%s）[%d]' % (lab, kind, i), '', v[kind], '']
        post = ''
        if '【後文背景' in pack[-1]['text']:
            post = '【後文背景' + pack[-1]['text'].split('【後文背景', 1)[1]
        if post:
            lines += ['', post.strip(), '']
        io.open(os.path.join(out, key + '.md'), 'w', encoding='utf-8').write('\n'.join(lines))
        index[key] = [x['key'] for x in pack]
        n += 1
    io.open(os.path.join(out, '索引_pack.json'), 'w', encoding='utf-8').write(
        json.dumps(index, ensure_ascii=False, indent=1))
    print('打包完成：%d 份材料（%d 個打包組，涵蓋 %d 組）→ %s'
          % (n, len(index), sum(len(v) for v in index.values()), out))


def _div(t):
    m = re.search(r'分歧與裁決[^\n]*\n(.+?)(?=\n[#*\s]*(?:3|三)[.、．：:]|\n\s*\**\s*修正後的譯文|\Z)', t, re.S)
    return re.sub(r'\n{3,}', '\n\n', m.group(1)).strip() if m else ''


def do_split(out, repdir, mat=None):
    index = json.load(io.open(os.path.join(out, '索引_pack.json'), encoding='utf-8'))
    rep = os.path.join(out, repdir)
    dst = os.path.join(out, '_拆回')
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(os.path.join(dst, '回覆'), exist_ok=True)
    ok = bad = 0
    for key, originals in index.items():
        p = os.path.join(rep, key + '_回.txt')
        if not os.path.exists(p):
            bad += 1
            continue
        t = io.open(p, encoding='utf-8').read()
        try:
            import build_a2 as A
            body3 = A.col3(t)
        except Exception:
            io.open(os.path.join(dst, '..', key + '_拆回異常.txt'), 'w', encoding='utf-8').write(t)
            bad += 1
            continue
        if MI.is_keep_a(body3):
            for ok_key in originals:
                io.open(os.path.join(dst, '回覆', ok_key + '_回.txt'), 'w', encoding='utf-8').write(
                    '## 1. 結論\n\n`PASS_A`\n\n## 2. 分歧與裁決\n\n兩譯本實質義理無分歧。\n\n'
                    '## 3. 修正後的譯文\n\nPASS_A_KEEP_A\n')
                if mat:
                    _emit_single(mat, dst, ok_key)
            ok += 1
            continue
        for _c, _f in (('【疏】', '【疏文】'), ('【記】', '【記文】'), ('【鈔】', '【鈔文】'),
                       ('【律】', '【律文】'), ('【註】', '【註文】'), ('【序】', '【序文】')):
            body3 = re.sub(r'(?m)^\s*' + _c, _f, body3)
        secs = re.split(r'【(' + LABS + r')】', body3)
        lab_map = {}
        if len(secs) >= 3:
            for i in range(1, len(secs) - 1, 2):
                lab_map[secs[i]] = lab_map.get(secs[i], '') + secs[i + 1]
            if secs[0].strip():
                lab_map['_head'] = secs[0]
                for _k in list(lab_map):
                    if _k != '_head':
                        lab_map[_k] = lab_map['_head'] + lab_map[_k]
                        lab_map.pop('_head', None)
                        break
        else:
            lab_map['_head'] = body3
        _jia_cache = {}
        def _jia_group(n):
            if n in _jia_cache:
                return _jia_cache[n]
            out = []
            if mat:
                _mp = os.path.join(mat, ok_key + '.md')
                if os.path.exists(_mp):
                    _mt = io.open(_mp, encoding='utf-8').read()
                    _jia = MI.from_jia(_mt)
                    for _lab, _body in re.findall(
                            r'【(疏文|記文|鈔文|律文|註文|序文)】\n(.+?)(?=\n【|\Z)', _jia, re.S):
                        out.append((_lab, _body.strip()))
                    if not out:
                        for _lab, _idx, _body in re.findall(
                                r'■ (疏文|記文|鈔文|律文|註文|序文)（譯本甲）\[(\d+)\]\s*\n+(.+?)(?=\n+■ |\n+【|\Z)',
                                _mt, re.S):
                            if int(_idx) == n:
                                out.append((_lab, _body.strip()))
            _jia_cache[n] = out
            return out
        per_group = {}
        for lab, chunk in lab_map.items():
            parts = re.split(r'(?m)^\s*`?\s*(?:[-*•]|\d+[.、])?\s*\[\s*(\d+)\s*\]\s*', chunk)
            for i in range(1, len(parts) - 1, 2):
                n = int(parts[i])
                lab2 = lab
                mm = re.match(r'\s*【(' + LABS + r')】', parts[i + 1])
                if mm:
                    lab2 = mm.group(1)
                    per_group.setdefault(n, []).append((lab2, parts[i + 1][mm.end():].strip()))
                else:
                    per_group.setdefault(n, []).append((lab2, parts[i + 1].strip()))
        div = _div(t)
        _by_i = {}
        for _ln in div.split('\n'):
            _m = re.match(r'\s*`?\s*(?:[-*•]|\d+[.、])?\s*\[\s*(\d+)\s*\]', _ln)
            if _m:
                _by_i.setdefault(int(_m.group(1)), []).append(_ln.strip())
        for i, ok_key in enumerate(originals, 1):
            _has_body = bool([b for a, b in per_group.get(i, []) if a != '_head' and b])
            if i not in _by_i and not _has_body and not _jia_group(i):
                io.open(os.path.join(dst, '回覆', ok_key + '_回.txt'), 'w', encoding='utf-8').write(
                    '## 1. 結論\n\nPASS_A\n\n## 2. 分歧與裁決\n\n兩譯本實質義理無分歧，沿用譯本甲。\n\n'
                    '## 3. 修正後的譯文\n\nPASS_A_KEEP_A\n')
                if mat:
                    _emit_single(mat, dst, ok_key)
                continue
            _d = chr(10).join(_by_i.get(i, []))
            segs = [(a, b) for a, b in per_group.get(i, []) if a != '_head' and b]
            if not segs:
                segs = _jia_group(i)
            if not segs:
                head = [b for a, b in per_group.get(i, []) if a == '_head' and b]
                if head:
                    segs = [('_nolabel', '\n'.join(head))]
                    body = segs[-1][1]
                else:
                    body = ''
            else:
                body = '\n\n'.join('【%s】\n%s' % (a, b) for a, b in segs)
            if not body:
                io.open(os.path.join(dst, '..', ok_key + '_拆回異常.txt'), 'w', encoding='utf-8').write(t)
                bad += 1
                continue
            txt = ('## 1. 結論\n\n`REVISED`\n\n## 2. 分歧與裁決\n\n%s\n\n'
                   '## 3. 修正後的譯文\n\n%s\n') % (_d or ('（同批輸出，本段未列分歧，沿用譯本甲）' if i not in _by_i else div) or '（同批次裁決）', body)
            io.open(os.path.join(dst, '回覆', ok_key + '_回.txt'), 'w', encoding='utf-8').write(txt)
            if mat:
                _emit_single(mat, dst, ok_key)
        ok += 1

    # 未打包的單組：材料與回覆一併帶入
    if not mat:
        for f in sorted(os.listdir(out)):
            if not f.endswith('.md') or f[:-len('.md')] in index:
                continue
            k = f[:-3]
            shutil.copy2(os.path.join(out, f), os.path.join(dst, f))
            _j = os.path.join(out, k + '.json')
            if os.path.exists(_j):
                shutil.copy2(_j, os.path.join(dst, k + '.json'))
    if mat:
        for f in sorted(os.listdir(out)):
            if not f.endswith('.md') or f[:-len('.md')] in index:
                continue
            k = f[:-3]
            _emit_single(out, dst, k)
            rp = os.path.join(rep, k + '_回.txt')
            if os.path.exists(rp):
                shutil.copy2(rp, os.path.join(dst, '回覆', k + '_回.txt'))
    print('拆回完成：%d 組成功、%d 組缺回覆 → %s' % (ok, bad, dst))

    if bad:
        raise SystemExit(3)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--materials', default='')
    ap.add_argument('--out', required=True)
    ap.add_argument('--mode', choices=['pack', 'split'], default='pack')
    ap.add_argument('--replies', default='回覆')
    ap.add_argument('--mat', default='')
    args = ap.parse_args()
    out = os.path.join(B, args.out.replace('/', os.sep))
    mat = os.path.join(B, args.mat.replace('/', os.sep)) if args.mat else (
        os.path.join(B, args.materials.replace('/', os.sep)) if args.materials else None)
    if args.mode == 'pack':
        do_pack(mat, out)
    else:
        do_split(out, args.replies, mat)


if __name__ == '__main__':
    main()
