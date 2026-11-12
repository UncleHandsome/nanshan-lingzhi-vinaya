# -*- coding: utf-8 -*-
"""r2 1073-1180 批次套用器（備份 _m4，自動以 COUNT 定位段號）。
用法:
  python _zx3_batch.py edits.tsv done.txt [--dry]
edits.tsv: n<TAB>seq<TAB>old<TAB>new<TAB>why
done.txt : 每行一個檔號（本批處理完畢，含無改動者）
另可選 doubt.tsv / rej.tsv 以供記錄（n<TAB>seq<TAB>text）
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

BKM4 = os.path.join(L.ROOT, '歸檔', 'r2修正前', '資持記')
LOGD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_zx3_log')
STAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_zx3_stat.tsv')


def backup_m4(book, chunk, src):
    d = BKM4 if book == '資持記' else os.path.join(BKM4, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + '_m4.txt')
    if not os.path.exists(dst):
        shutil.copy2(src, dst)


def main():
    ep = sys.argv[1]
    dp = sys.argv[2]
    dry = '--dry' in sys.argv
    rows = []
    for ln in open(ep, encoding='utf-8-sig'):
        ln = ln.rstrip('\n').rstrip('\r')
        if not ln.strip() or ln.startswith('#'):
            continue
        p = ln.split('|||')
        if len(p) < 5:
            raise SystemExit('BAD ROW %r' % ln)
        rows.append(dict(n=int(p[0]), seq=int(p[1]), old=p[2], new=p[3], why=p[4]))
    dones = []
    for ln in open(dp, encoding='utf-8-sig'):
        ln = ln.strip()
        if ln:
            dones.append(int(ln))
    byn = {}
    for r in rows:
        byn.setdefault(r['n'], []).append(r)
    cache = {}
    total_edits = 0
    bad = []
    for n in dones:
        recs = L.parse_review(n)
        segmap = {r['seq']: (r['book'], r['chunk'], r['seg']) for r in recs}
        es = byn.get(n, [])
        # group by chunk
        bychunk = {}
        relocs = []
        for e in es:
            if e['seq'] not in segmap:
                bad.append((n, e['seq'], 'BADSEQ', e['old'][:40]))
                continue
            book, chunk, seg = segmap[e['seq']]
            key = (book, chunk)
            if key not in cache:
                cache[key] = L.Out(book, chunk)
            o = cache[key]
            if o.segs[seg - 1].count(e['old']) != 1:
                found = [i + 1 for i, t in enumerate(o.segs) if t.count(e['old']) == 1]
                if len(found) != 1:
                    bad.append((n, e['seq'], 'CAND%s' % found, e['old'][:40]))
                    continue
                relocs.append((e['seq'], seg, found[0]))
                seg = found[0]
            bychunk.setdefault(key, []).append(dict(seg=seg, old=e['old'], new=e['new'], why=e['why']))
        logs = []
        for (book, chunk), ces in bychunk.items():
            o = cache[(book, chunk)]
            segs = list(o.segs)
            for e in sorted(ces, key=lambda x: x['seg']):
                i = e['seg'] - 1
                t = segs[i]
                if t.count(e['old']) != 1:
                    raise SystemExit('COUNT %d %s#%d old=%r' % (t.count(e['old']), chunk, e['seg'], e['old'][:80]))
                nl0 = t.count('\n') + t.count('\r')
                t2 = t.replace(e['old'], e['new'])
                if t2.count('\n') + t2.count('\r') != nl0:
                    raise SystemExit('NEWLINE %s#%d' % (chunk, e['seg']))
                segs[i] = t2
                logs.append(dict(book=book, chunk=chunk, seg=e['seg'], old=e['old'], new=e['new'], why=e['why']))
            o.segs = segs
            if not dry:
                backup_m4(book, chunk, o.path)
                o.save()
        total_edits += len(logs)
        if not dry:
            os.makedirs(LOGD, exist_ok=True)
            with open(os.path.join(LOGD, 'log_%d.json' % n), 'w', encoding='utf-8') as f:
                json.dump(dict(n=n, edits=logs, relocs=relocs), f, ensure_ascii=False, indent=1)
        print('%d: %d edits%s' % (n, len(logs), (' RELOC ' + str(relocs)) if relocs else ''))
        if not dry:
            L.append_done(n)
    print('TOTAL files=%d edits=%d bad=%d' % (len(dones), total_edits, len(bad)))
    for b in bad:
        print('BAD %d seq%d %s old=%r' % b)


if __name__ == '__main__':
    main()
