# -*- coding: utf-8 -*-
"""套用「斷句／段落邊界」AI 回覆：把上一列結尾的指定片段搬到下一列開頭。

回覆格式（見 斷句材料_20261126/_說明.md）：
<<<JSONL_START>>>
{"key":"資持記／381","status":"move|keep","moved_source":"...","moved_translation":"...","note":"..."}
<<<JSONL_END>>>

安全規則：
* moved_source 必須是該列 source 結尾的逐字子字串（rstrip 後精確符合）。
* moved_translation 必須是該列 translation 結尾的逐字子字串。
* 不拆字、不改字、不用比例、不猜測；任何一項驗證失敗即整筆略過並報錯。
* 搬移後 raw_start/raw_end 以漢字數調整，並驗證六書文字總序不變。
"""
import argparse
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOK_CN = {'行事鈔': 'xingshichao', '戒疏': 'jieshu', '業疏': 'yeshu',
           '資持記': 'zhichi', '尼鈔': 'nicao', '義鈔': 'yichao'}
LABEL_RE = re.compile(r'^(【[^】]+】\s*\n?)')
HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return ''.join(HAN.findall(s or ''))


def prepend_seg(seg, src, tr):
    s = seg.get('source') or ''
    t = seg.get('translation') or ''
    ms = LABEL_RE.match(s)
    if ms:
        seg['source'] = ms.group(1) + src + s[ms.end():]
    else:
        seg['source'] = src + s
    mt = LABEL_RE.match(t)
    if mt:
        seg['translation'] = mt.group(1) + tr + '\n' + t[mt.end():]
    else:
        seg['translation'] = tr + '\n' + t


def rebuild_row(r):
    segs = r.get('segments') or []
    old = r.get('source') or ''
    r['source'] = ''.join(s.get('source') or '' for s in segs)
    r['translation'] = '\n\n'.join(s.get('translation') or '' for s in segs)
    r['display_source'] = r['source'] if r.get('display_source') == old else r['source'].rstrip('。；，、')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('reply')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    text = io.open(a.reply, encoding='utf-8').read()
    items = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln.startswith('{'):
            continue
        try:
            items.append(json.loads(ln))
        except Exception as e:
            print('JSON 解析失敗，略過：', ln[:60], e)
    print('回覆筆數：', len(items))

    books = {}
    errors = 0
    applied = []
    for it in items:
        key = str(it.get('key') or '').strip()
        if '／' in key:
            cn, k = key.split('／', 1)
        elif '/' in key:
            cn, k = key.split('/', 1)
        else:
            print('缺少書名，略過：', key)
            errors += 1
            continue
        bk = BOOK_CN.get(cn.strip())
        if not bk:
            print('未知書名，略過：', cn)
            errors += 1
            continue
        books.setdefault(bk, []).append((k.strip(), it))

    for bk, lst in books.items():
        p = os.path.join(B, '定稿', bk + '.jsonl')
        rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
        old_src = ''.join(r.get('source') or '' for r in rows)
        old_tr = re.sub(r'【[^】]+】', '', ''.join(r.get('translation') or '' for r in rows))
        changed = 0
        for k, it in lst:
            if str(it.get('status')) != 'move':
                continue
            idx = [i for i, r in enumerate(rows) if str(r.get('key')) == k]
            if len(idx) != 1:
                print('[%s %s] 找不到唯一列，略過' % (bk, k))
                errors += 1
                continue
            i = idx[0]
            if i + 1 >= len(rows):
                print('[%s %s] 沒有下一列，略過' % (bk, k))
                errors += 1
                continue
            r, nxt = rows[i], rows[i + 1]
            ms = (it.get('moved_source') or '').rstrip()
            mt = (it.get('moved_translation') or '').rstrip()
            if not ms or not mt:
                print('[%s %s] 缺 moved_source／moved_translation，略過' % (bk, k))
                errors += 1
                continue
            src = (r.get('source') or '').rstrip()
            tr = r.get('translation') or ''
            trs = tr.rstrip()
            if src == ms:
                print('[%s %s] 整列內容就是這句引語，搬走會變空列→保留不動' % (bk, k))
                continue
            if not src.endswith(ms):
                print('[%s %s] moved_source 不是結尾子字串，略過' % (bk, k))
                errors += 1
                continue
            if not trs.endswith(mt):
                print('[%s %s] moved_translation 不是白話結尾子字串，略過' % (bk, k))
                errors += 1
                continue
            segs = r.get('segments') or []
            last = segs[-1]
            lsrc = (last.get('source') or '').rstrip()
            ltr = (last.get('translation') or '').rstrip()
            if not lsrc.endswith(ms):
                print('[%s %s] 最後分段結尾不符，略過' % (bk, k))
                errors += 1
                continue
            if not ltr.endswith(mt):
                print('[%s %s] 最後分段白話結尾不符，略過' % (bk, k))
                errors += 1
                continue
            moved_han = len(han(ms))
            # 從最後分段切除
            last['source'] = lsrc[:-len(ms)].rstrip()
            last['translation'] = ltr[:-len(mt)].rstrip()
            # 搬到下一列同段別（或最後分段）
            label = last.get('label')
            tgt = None
            for s in nxt.get('segments') or []:
                if s.get('label') == label:
                    tgt = s
                    break
            tgt = tgt if tgt is not None else (nxt.get('segments') or [None])[-1]
            if tgt is None:
                print('[%s %s] 下一列沒有分段，略過' % (bk, k))
                errors += 1
                continue
            prepend_seg(tgt, ms, mt)
            r['raw_end'] = r['raw_end'] - moved_han
            nxt['raw_start'] = nxt['raw_start'] - moved_han
            rebuild_row(r)
            rebuild_row(nxt)
            changed += 1
            applied.append((bk, k, ms, mt))

        new_src = ''.join(r.get('source') or '' for r in rows)
        new_tr = re.sub(r'【[^】]+】', '', ''.join(r.get('translation') or '' for r in rows))
        flat = lambda s: re.sub(r'\s', '', s)
        if flat(new_src) != flat(old_src):
            print('[%s] 警告：來源文字總序改變！不寫入' % bk)
            sys.exit(1)
        if flat(new_tr) != flat(old_tr):
            print('[%s] 警告：白話文字總序改變！不寫入' % bk)
            sys.exit(1)
        if not a.dry:
            io.open(p, 'w', encoding='utf-8', newline='\n').writelines(
                json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
        print('[%s] 套用 %d 筆%s' % (bk, changed, '（dry-run）' if a.dry else ''))

    print('\n=== 套用明細 ===')
    for x in applied:
        print('[%s %s] %r || %r' % (x[0], x[1], x[2], x[3][:40]))
    if errors:
        print('\n有 %d 筆驗證失敗（未寫入）' % errors)


if __name__ == '__main__':
    main()
