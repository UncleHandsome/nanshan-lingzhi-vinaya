# -*- coding: utf-8 -*-
"""句級合編 v2 → docs/hebian/*.html

對位改用「文意對位」結果 pairs_v2_index.json（1:1 / 1:n / n:1 / n:m 皆支援），
不再用舊 hb_align 的段號推算。

版面沿用 site_hebian 的 emit_pair（鈔文／記文＋白話並列），
差別只在「誰配誰」由 pairs_v2 決定：
  逐條鈔段 → 先出鈔（含白話）→ 再出所有對到它的記段（可多段）
  沒有對到任何鈔段的記段（orphan）→ 補在該篇／該卷末，並標示「無對應鈔段」

篇題釋鏈（2026-11-27）
---------------------
每一篇的「釋○篇」記文（part='head'）及其後續仍屬釋篇名的記段，必須整串排在
該篇第一個鈔段之前，順序為 head → 續段…。續段判定為通用規則（不再硬編碼）：
依記文原序納入同篇後續段，直到
  1. 段內出現「敘意中／敘來意／來意中／敘意／科判／標歎中／歎教文中／釋文」
     等邊界標記：標記在段首則該段不提前；標記在段中則整段提前後停止
     （記段不可切）；
  2. 或該段已對到本篇鈔段（表示已開始逐句釋鈔）。
見 HEAD_BOUNDARY 與 build_head_chains()。
"""
import bisect
import collections
import io
import json
import os

import site_assets as SA
import site_hebian as SH

B = SH.B
SITE = SH.SITE
OUT = SH.OUT
HB = SH.HB
PAIRS = os.path.join(B, '定稿', '對位結果_20261125', 'pairs_v2_index.json')
SEGMAP_PATH = os.path.join(B, '定稿', '對位結果_20261125', 'seg_groups.json')

# 「釋○篇」之後，記文由釋篇名轉入敘意／釋文的邊界標記。
# 標記在段首：該段屬敘意／釋文，不提前；標記在段中：整段提前後停止（段不可切）。
HEAD_BOUNDARY = ('敘意中', '敘來意', '來意中', '敘意', '科判', '標歎中',
                 '歎教文中', '釋文')


def build_head_chains(ji, ji2c, chao_chapter):
    """回傳 {ch: [ji 索引, ...]}：每一篇「篇題釋」記文鏈（head 起）。

    規則（通用，無硬編碼）：
      * 從 part='head' 的記段起，依記文原序只納入同篇（ch 相同）的後續段；
      * 遇到段內含 HEAD_BOUNDARY 標記者：段首 → 不納入並停止；
        段中 → 整段納入後停止（該段同時是篇題釋尾巴，不可切）；
      * 遇到已對到「本篇鈔段」的記段（開始逐句釋鈔）→ 不納入並停止；
      * 其餘同篇後續段仍屬釋篇名，納入。
    """
    chains = {}
    for ch in sorted({u['ch'] for u in ji if u.get('part') == 'head'}):
        head = next(i for i, u in enumerate(ji)
                    if u['ch'] == ch and u['part'] == 'head')
        chain = [head]
        for i in range(head + 1, len(ji)):
            u = ji[i]
            if u['ch'] != ch:
                break
            src = u['source']
            hit = next((m for m in HEAD_BOUNDARY if m in src), None)
            mpos = src.find(hit) if hit else -1
            on_chao = any(chao_chapter.get(str(t)) == ch
                          for t in (ji2c.get(str(u['key'])) or []))
            # 「科判」字樣本身不足以判為釋鈔正文（篇題釋也可能提到科判）；
            # 僅當該段已對到本篇鈔段、且段中含科判時，才留在鈔文後（如記文 450）。
            if '科判' in src and on_chao:
                break
            if mpos == 0:
                break
            if mpos > 0:
                chain.append(i)
                break
            if on_chao:
                break
            chain.append(i)
        chains[ch] = chain
    return chains


def main():
    hraw, bounds = SH.volume_bounds()
    xs = SH.load_jsonl('xingshichao')
    zc = SH.load_jsonl('zhichi')
    chao, titles = SH.build_chao(xs, hraw, bounds)
    ji, _anchors = SH.build_ji(zc)

    idx = json.load(io.open(PAIRS, encoding='utf-8'))
    c2j = idx['chao2ji']
    ji2c = idx['ji2chao']

    # key → unit 索引
    ch_by_key = collections.defaultdict(list)
    for i, u in enumerate(chao):
        ch_by_key[str(u['key'])].append(i)
    ji_by_key = collections.defaultdict(list)
    for i, u in enumerate(ji):
        ji_by_key[str(u['key'])].append(i)

    # 章 → 卷（第一篇出現的卷）
    chap_vol = {}
    for u in chao:
        if u['chapter'] and u['chapter'] not in chap_vol:
            chap_vol[u['chapter']] = u['vol']

    # 記段排序用（同一鈔段的多個記段，依記段在書中的先後）
    ji_order = {i: n for n, i in enumerate(range(len(ji)))}

    # 每卷要輸出的鈔 unit（依序）
    by_vol = collections.defaultdict(list)
    for i, u in enumerate(chao):
        by_vol[u['vol']].append(i)

    # 實際存在於合編頁面的鈔段 key（篇題列會被 build_chao 排除）
    chao_unit_keys = {str(u['key']) for u in chao}

    # ── 句段級對位 ──────────────────────────────────────────────
    # 一個鈔段（定稿單位）依 segments 拆成數個句段 pair；
    # 記段預設只「掛在整個鈔段之後」，若 seg_groups.json 有指定，
    # 則改為掛在它所解釋的那一句段之下。
    segmap = {}
    if os.path.exists(SEGMAP_PATH):
        segmap = {k: v for k, v in json.load(io.open(SEGMAP_PATH, encoding='utf-8')).items()
                  if not k.startswith('_')}

    key_pos = {}
    key_last_seq = {}
    for u in chao:
        k = str(u['key'])
        key_pos.setdefault(k, u['pos'])
        key_last_seq[k] = max(key_last_seq.get(k, 0), u['seq'])

    # 每個記段的落點：(鈔 key, 句段序號 1 起；None = 整段最後；'tail' = 鈔文後延伸)
    ji_target = {}
    for i, u in enumerate(ji):
        k = str(u['key'])
        targets = [t for t in (ji2c.get(k) or []) if t in chao_unit_keys]
        if not targets:
            continue
        t = min(targets, key=lambda x: key_pos.get(x, 1 << 30))
        ji_target[i] = (t, None)
    for ckey, spec in segmap.items():
        for s, jkeys in (spec.get('groups') or {}).items():
            for jk in jkeys:
                for jidx in ji_by_key.get(str(jk), []):
                    if ji_target.get(jidx, (None,))[0] == ckey:
                        ji_target[jidx] = (ckey, int(s))
        for jk in ((spec.get('tail') or {}).get('keys') or []):
            for jidx in ji_by_key.get(str(jk), []):
                if ji_target.get(jidx, (None,))[0] == ckey:
                    ji_target[jidx] = (ckey, 'tail')

    # 記文「新篇開頭」(part=head，如「2 釋集僧篇…」) 應掛到該篇的第一個鈔段，
    # 不能只依 unit key 的對位全掛在上一篇（否則第2篇開頭會漏在標宗篇）。
    # 同時，若某記段的章（ch）與對位到的鈔段章不同（跨篇切段，如 448 尾段之後的 449），
    # 一律改掛到該章第一個鈔段，確保整段篇頭與其後文都在同一篇頁、順序連續。
    chao_chapter = {str(x['key']): x.get('chapter') for x in chao}
    # 篇題釋鏈：每篇從「釋○篇」head 起，到敘意／釋文之前的記段（通用判定）
    head_chains = build_head_chains(ji, ji2c, chao_chapter)
    for i, u in enumerate(ji):
        ch = u.get('ch')
        if not ch:
            continue
        cur = ji_target.get(i)
        if u.get('part') != 'head' and cur and chao_chapter.get(cur[0]) == ch:
            continue
        cks = [k for k, c in chao_chapter.items() if c == ch]
        if not cks:
            continue
        ck = min(cks, key=lambda k: key_pos.get(k, 1 << 30))
        ji_target[i] = (ck, None)

    target_ji = collections.defaultdict(list)
    for jidx, tgt in ji_target.items():
        target_ji[tgt].append(jidx)
    for v in target_ji.values():
        v.sort()

    # orphan 記段：沒有鈔段對到，或對到的鈔段不在頁面上（如篇題列）
    orphan_by_vol = collections.defaultdict(list)
    for i, u in enumerate(ji):
        k = str(u['key'])
        targets = ji2c.get(k) or []
        if targets and any(t in chao_unit_keys for t in targets):
            continue
        v = chap_vol.get(u['ch']) or HB[0]
        orphan_by_vol[v].append(i)

    emitted_ji = set()
    stats = dict(vols=0, sections=0, pairs=0, chao=0, ji=0, orphan=0, multi=0)
    nav_vols = []

    for vi, vol in enumerate(HB):
        body = []
        toc = []
        cur_ch = None
        used_ids = set()

        def emit_chao(uidx, many=False):
            u = chao[uidx]
            h = SH.emit_pair(u, '鈔', 0, used_ids)
            if many:
                h = h.replace('class="pair c"', 'class="pair c has-many"', 1)
            body.append(h)
            stats['chao'] += 1

        def emit_ji(jidx, note='', tie=False):
            if jidx in emitted_ji:
                return
            emitted_ji.add(jidx)
            u = ji[jidx]
            h = SH.emit_pair(u, '記', 0, used_ids)
            if tie:
                h = h.replace('class="pair j"', 'class="pair j tie"', 1)
            body.append(h)
            stats['ji'] += 1
            if note:
                body.append('<div class="pair j"><div class="t">（%s）</div></div>' % note)

        for uidx in by_vol[vol]:
            u = chao[uidx]
            ch = u['chapter']
            if ch != cur_ch:
                cur_ch = ch
                if ch:
                    name = titles.get(ch, (0, '', None))[1]
                    label = '%s篇' % name if name else ('第 %d 篇' % ch)
                    toc.append(['p%d' % ch, label])
                    body.append('<h2 class="sec" id="p%d">%s</h2>' % (ch, SH.esc(label)))
                    stats['sections'] += 1
                    # 篇題釋鏈（head→續段…）整串排在該篇第一個鈔段之前，
                    # 續段判定見 build_head_chains()（不再硬編碼 EXTRA_HEAD）。
                    for jidx in head_chains.get(ch, []):
                        emit_ji(jidx)
            k = str(u['key'])
            spec = segmap.get(k)
            # 這一句段之下要掛的記段
            group = target_ji.get((k, u['seq'] + 1), []) if spec else []
            is_last = u['seq'] >= key_last_seq.get(k, 0)
            # 沒有句段級指定的記段，一律接在整個鈔段最後
            rest = target_ji.get((k, None), []) if is_last else []
            todo = [j for j in group + rest if j not in emitted_ji]
            emit_chao(uidx, many=len(todo) > 1)
            for jidx in todo:
                emit_ji(jidx, tie=True)
            if todo:
                stats['pairs'] += 1
                if len(todo) > 1:
                    stats['multi'] += 1
            if is_last and spec:
                tail = spec.get('tail') or {}
                tkeys = [j for jk in (tail.get('keys') or [])
                         for j in ji_by_key.get(str(jk), [])]
                tkeys = [j for j in tkeys if j not in emitted_ji]
                if tkeys:
                    if tail.get('note'):
                        body.append('<p class="hint">%s</p>' % SH.esc(tail['note']))
                    for jidx in tkeys:
                        emit_ji(jidx, tie=True)
                    stats['pairs'] += 1
                    if len(tkeys) > 1:
                        stats['multi'] += 1

        # 本卷 orphan 補在卷末
        for jidx in sorted(orphan_by_vol.get(vol, []), key=lambda x: ji_order[x]):
            u = ji[jidx]
            if jidx in emitted_ji:
                continue
            emitted_ji.add(jidx)
            body.append(SH.emit_pair(u, '記', 0, used_ids))
            stats['ji'] += 1
            stats['orphan'] += 1

        if not body:
            raise SystemExit('%s 沒有內容' % vol)
        prev = HB[vi - 1] if vi > 0 else None
        nxt = HB[vi + 1] if vi + 1 < len(HB) else None
        ttl = '四分律行事鈔資持記・句級合編　' + vol
        body_html = ('<h1>' + SH.esc(ttl) + '</h1>'
                     '<p class="byline">鈔文（淺褐）、記文（淺藍）與白話逐段並列；'
                     '對位依文意判定，允許一對多。原文 CBETA，白話本站。</p>'
                     + '\n'.join(body))
        out = SA.page(ttl, body_html, prefix='../',
                      prev_url=(prev + '.html' if prev else None),
                      next_url=(nxt + '.html' if nxt else None),
                      prev_label=prev, next_label=nxt, current_label=vol,
                      book_label='四分律行事鈔資持記・句級合編', book_short='合編',
                      pager=True, tools=True,
                      description='四分律行事鈔資持記・句級合編　%s：鈔文、記文與白話逐段對照。' % vol)
        if '<br><br>' in out:
            raise SystemExit('出現 <br><br>')
        io.open(os.path.join(OUT, vol + '.html'), 'w', encoding='utf-8', newline='\n').write(out)
        stats['vols'] += 1
        nav_vols.append(dict(v=vol, secs=[list(x) for x in toc]))
        print(vol, '篇', len(toc), 'body', len(body), flush=True)

    # 未輸出的記段（理論上不該有）
    left = [i for i in range(len(ji)) if i not in emitted_ji]
    if left:
        print('WARN 未輸出記段 %d：%s' % (len(left), left[:10]))

    # 先更新 nav.json（合編卷條目＝剛重繪的完整卷頁，secs 暫不帶篇頁 stem），
    # 再重建合編搜尋索引：book_volumes() 才不會拿上一次切篇留下的舊篇頁來索引。
    # 之後 split_by_section.py 會把 secs 補上篇頁 stem，最後全站索引再重建一次。
    np = os.path.join(SITE, 'nav.json')
    nav = json.load(io.open(np, encoding='utf-8'))
    for b in nav.get('books', []):
        if b.get('out') == 'hebian':
            b['vols'] = nav_vols
            b['title'] = '四分律行事鈔資持記・句級合編'
            break
    tmp = np + '.tmp'
    io.open(tmp, 'w', encoding='utf-8').write(json.dumps(nav, ensure_ascii=False, indent=1) + '\n')
    os.replace(tmp, np)

    import build_search_index as BSI
    BSI.build(site=SITE, only=['hebian'], quiet=True)

    print(json.dumps(stats, ensure_ascii=False))
    return stats


if __name__ == '__main__':
    main()
