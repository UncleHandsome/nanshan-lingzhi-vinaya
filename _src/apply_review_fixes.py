# -*- coding: utf-8 -*-
"""把校閱報告的「建議」套回 AI語譯/out。

用法：
    python _src/apply_review_fixes.py report_1          # 預覽
    python _src/apply_review_fixes.py report_1 --apply  # 寫回

規則：
  A 型「將「A」改為「B」」：A 必須在現行段落中，直接替換 A→B。
  B 型「補譯／改譯／整段…「B」」：以 B 取代整段。
  C 型其餘（只說「應改寫」而沒給文字）：不套用，列為待人工。
寫回前會備份到 AI語譯/_work/review/backup_<report>/。
"""
import os, io, re, sys, csv, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(B, 'AI語譯', '_work', 'review')

Q = r'「([^」]{2,})」'


def _norm(s):
    return re.sub(r'[\s，。、；：？！「」『』（）()〔〕\[\]〈〉《》`*]', '', s)


def _ratio(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def common_suffix(a, b):
    n = 0
    while n < len(a) and n < len(b) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def parse_suggestion(s):
    """回傳 (kind, a, b)。"""
    m = re.search(r'「([^」]+)」\s*(?:修改|修正|更正|改)?為\s*「([^」]+)」', s)
    if m:
        return 'A', m.group(1), m.group(2)
    for kw in ('補譯為白話', '補譯為', '改譯為', '整段改譯為', '改為', '修改為', '作'):
        m = re.search(kw + r'\s*[:：]?\s*「([^」]+)」', s)
        if m:
            return 'B', None, m.group(1)
    return 'C', None, None


def load_out(book, chunk):
    p = os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt')
    return p, [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def main():
    name = sys.argv[1]
    if name.startswith('report_'):
        name = name[len('report_'):]
    apply = '--apply' in sys.argv
    rows = list(csv.DictReader(io.open(os.path.join(RV, 'report_%s.tsv' % name), encoding='utf-8'), delimiter='\t'))

    # 修訂者產出的整段替換（優先於自動規則）
    over = {}
    if '--overrides' in sys.argv:
        for f in sys.argv[sys.argv.index('--overrides') + 1].split(','):
            fp = f if os.path.isabs(f) else os.path.join(B, f)
            if not os.path.exists(fp):
                continue
            for r in csv.reader(io.open(fp, encoding='utf-8'), delimiter='\t'):
                if len(r) < 4 or r[0] == 'book':
                    continue
                over[(r[0], r[1], int(r[2]))] = r[3]

    todo = {}
    skipped = []
    done_prev = set()
    apf = os.path.join(RV, 'applied_%s.tsv' % name)
    if os.path.exists(apf):
        for r in csv.DictReader(io.open(apf, encoding='utf-8'), delimiter='\t'):
            done_prev.add((r['chunk'], int(r['seg'])))
    for r in rows:
        p, ps = load_out(r['book'], r['chunk'])
        seg = int(r['seg']) - 1
        # TSV 的 seg 是來源段號；若 status 是 shift:N 以 N 為準
        if r['status'].startswith('shift:'):
            seg = int(r['status'].split(':')[1]) - 1
        if not (0 <= seg < len(ps)):
            skipped.append((r, 'seg out of range'))
            continue
        cur = ps[seg]
        key = (r['book'], r['chunk'], seg + 1)
        if (r['chunk'], seg + 1) in done_prev:
            continue
        if key in over:
            new = over[key]
            src = 'override'
        else:
            kind, a, b = parse_suggestion(r['suggestion'])
            if kind == 'A':
                if a not in cur:
                    skipped.append((r, 'anchor not found'))
                    continue
                new = cur.replace(a, b, 1)
                src = 'A'
            elif kind == 'B':
                # 整段替換只有在「整段很短」或「整段就是原文照抄」時才安全；
                # 長段落裡的單句建議交給修訂者處理，否則會吃掉前半段。
                r_ov = _ratio(r['orig'], cur)
                if len(cur) > 300 and r_ov < 0.85:
                    # 先試「原文尾巴照抄」：把被照抄的尾段換成建議譯文
                    n = common_suffix(cur, r['orig'])
                    if n >= 15:
                        new = cur[:len(cur) - n] + b
                        src = 'T'
                        todo.setdefault(p, []).append((seg, new, r, src))
                        continue
                    skipped.append((r, 'clause in long para (overlap %.2f, len %d)' % (r_ov, len(cur))))
                    continue
                if len(b) < 0.7 * len(cur):
                    skipped.append((r, 'short replacement %d/%d' % (len(b), len(cur))))
                    continue
                new = b
                src = 'B'
            else:
                skipped.append((r, 'no quoted replacement'))
                continue
        todo.setdefault(p, []).append((seg, new, r, src))

    n = sum(len(v) for v in todo.values())
    print('可套用 %d 條，略過 %d 條' % (n, len(skipped)))
    for r, why in skipped:
        print('  SKIP %s#%s %s：%s' % (r['chunk'], r['seg'], r['level'], why))
    for p, lst in todo.items():
        print('  %s：%d 段' % (os.path.basename(p), len(lst)))

    if not apply:
        return
    bak = os.path.join(RV, 'backup_%s' % name)
    os.makedirs(bak, exist_ok=True)
    log = []
    for p, lst in todo.items():
        ps = [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
        shutil.copy2(p, os.path.join(bak, os.path.basename(p)))
        for seg, new, r, src in lst:
            old = ps[seg]
            ps[seg] = new
            log.append((r['book'], r['chunk'], seg + 1, r['level'], src, old, new))
        io.open(p, 'w', encoding='utf-8').write('\n\n'.join(ps) + '\n')
    with io.open(os.path.join(RV, 'applied_%s.tsv' % name), 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['book', 'chunk', 'seg', 'level', 'src', 'old', 'new'])
        for row in log:
            w.writerow(row)
    print('已套用', len(log), '條；備份', bak)


if __name__ == '__main__':
    main()
