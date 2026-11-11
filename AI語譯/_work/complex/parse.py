# -*- coding: utf-8 -*-
"""Parse complex batch review results + build segment / current-text indexes."""
import re, os, sys, json, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

# ---------- 1. segment index from 校閱_10K (1..549) ----------
def _num(p):
    m = re.search(r'(\d+)\.txt$', p)
    return int(m.group(1)) if m else 0

def build_segidx():
    labels, codes = {}, {}
    files = sorted(glob.glob(os.path.join(ROOT, '校閱_10K', '校閱_*.txt')), key=_num)[:549]
    for mf in files:
        t = read(mf)
        i = t.find('# 材料開始')
        if i < 0:
            continue
        seg = t[i:]
        parts = re.split(r'(?m)^【(\d{3}-\d{4})】(.+)$', seg)
        for j in range(1, len(parts), 3):
            code, label, body = parts[j], parts[j+1].strip(), parts[j+2]
            om = re.search(r'【原文】(.*?)(?=【譯文】|\Z)', body, re.S)
            tm = re.search(r'【譯文】(.*)', body, re.S)
            rec = {
                'code': code, 'label': label,
                'src': (om.group(1).strip() if om else ''),
                'tr': (tm.group(1).strip() if tm else ''),
                'mat': os.path.basename(mf),
            }
            labels[label] = rec
            codes[code] = rec
    return labels, codes

# ---------- 2. current text from AI語譯/out ----------
def split_blocks(t):
    return [b.strip('\n') for b in re.split(r'\n[ \t]*\n', t) if b.strip()]

def build_cur():
    cur = {}
    for f in glob.glob(os.path.join(ROOT, 'AI語譯', 'out', '**', '*.txt'), recursive=True):
        book = os.path.basename(os.path.dirname(f))
        if book.startswith('_'):
            continue
        chunk = os.path.splitext(os.path.basename(f))[0]
        blocks = split_blocks(read(f))
        for n, b in enumerate(blocks, 1):
            cur['%s/%s#%d' % (book, chunk, n)] = b
    return cur

# ---------- 3. parse resp files ----------
FIELD = ['原文起首', '問題', '依據', '建議', '信心', '疑點', '說明', '原文', '譯文', '自我反駁', '建議（若改）']
FIELD_RE = re.compile(r'^[-*]\s*(' + '|'.join(re.escape(x) for x in FIELD) + r')\s*[：:]\s*(.*)$')

def split_label(label):
    m = re.match(r'^(.+?)/([^/#]+)#(\d+)$', label)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    return None

def parse_resp():
    items = []
    files = sorted(glob.glob(os.path.join(ROOT, 'batch_qwen', 'r1_complex', 'resp_*.txt')))
    for f in files:
        base = os.path.basename(f)
        lines = read(f).split('\n')
        cur = None          # current item
        section = 'find'    # 'find' or 'doubt'
        in_end = False
        for raw in lines:
            line = raw.rstrip()
            s = line.strip()
            if not s:
                if cur is not None:
                    cur['_last'] = None
                continue
            if s.startswith('=== 本檔結束'):
                in_end = True
                if cur:
                    items.append(cur); cur = None
                continue
            if in_end:
                continue
            # header
            if s.startswith('### '):
                h = s[4:].strip()
                if cur:
                    items.append(cur); cur = None
                if '存疑' in h and len(h.split('｜')) < 4:
                    section = 'doubt'
                    hdr = {'file': base, 'section': 'doubt', 'rawhead': h, 'code': '', 'label': '', 'pl': '', 'ptype': '',
                           'hd_start': 0, 'hd_problem': 0, 'hd_basis': 0, 'hd_sugg': 0}
                    # may embed a label
                    for part in h.split('｜'):
                        if '#' in part and '/' in part:
                            hdr['label'] = part.strip()
                        elif re.match(r'^\d{3}-\d{4}$', part.strip()):
                            hdr['code'] = part.strip()
                        elif part.strip() == '存疑':
                            hdr['pl'] = '存疑'
                    hdr['_last'] = None
                    cur = hdr
                    continue
                section = 'find'
                parts = [x.strip() for x in h.split('｜')]
                code = parts[0] if re.match(r'^\d{3}-\d{4}$', parts[0]) else ''
                it = {'file': base, 'section': 'find', 'rawhead': h, 'code': code,
                      'label': parts[1] if len(parts) > 1 else '',
                      'pl': parts[2] if len(parts) > 2 else '',
                      'ptype': '｜'.join(parts[3:]) if len(parts) > 3 else '',
                      'hd_start': 0, 'hd_problem': 0, 'hd_basis': 0, 'hd_sugg': 0, '_last': None}
                it['ptype'] = it['ptype'].replace('**', '').strip(' *')
                it['pl'] = it['pl'].replace('**', '').strip()
                cur = it
                continue
            if s.startswith('---'):
                if cur:
                    items.append(cur); cur = None
                continue
            if s.startswith('【存疑】') or (s.startswith('**存疑') and s.rstrip('*').endswith('**')):
                if cur:
                    items.append(cur); cur = None
                section = 'doubt'
                continue
            m = FIELD_RE.match(s)
            if m:
                if cur is None:
                    # stray field line (rare); start an anonymous doubt item
                    cur = {'file': base, 'section': 'doubt', 'rawhead': '(stray)', 'code': '', 'label': '', 'pl': '存疑',
                           'ptype': '', 'hd_start': 0, 'hd_problem': 0, 'hd_basis': 0, 'hd_sugg': 0, '_last': None}
                k = m.group(1)
                if k == '建議（若改）':
                    k = '建議'
                if k in ('原文起首', '問題', '依據', '建議', '疑點', '原文', '譯文', '說明', '自我反駁') and cur.get(k):
                    k = k  # keep first; still append
                cur.setdefault(k, '')
                cur[k] = (cur[k] + ' ' + m.group(2).strip()).strip() if cur.get(k) else m.group(2).strip()
                cur['_last'] = k
                continue
            # bullet line in doubt section: "- 001-0003｜label：..." or "- 006-0001：「...」"
            if section == 'doubt' and s.startswith('- '):
                body = s[2:].strip()
                mm = re.match(r'^(\d{3}-\d{4})?[（(]?([^：（）()]*?)[）)]?\s*[：:]\s*(.+)$', body)
                if mm:
                    if cur:
                        items.append(cur); cur = None
                    code = mm.group(1) or ''
                    mid = (mm.group(2) or '').strip()
                    label = ''
                    lm = re.search(r'([\u4e00-\u9fff0-9_]+/[^#\s：]+#\d+)', mid)
                    if lm:
                        label = lm.group(1)
                    cur = {'file': base, 'section': 'doubt', 'rawhead': body[:40], 'code': code, 'label': label,
                           'pl': '存疑', 'ptype': '', 'hd_start': 0, 'hd_problem': 0, 'hd_basis': 0, 'hd_sugg': 0,
                           '問題': mm.group(3).strip(), '_last': '問題'}
                    continue
            # continuation
            if cur is not None:
                k = cur.get('_last')
                if k:
                    cur[k] = (cur.get(k, '') + s).strip()
                else:
                    cur['問題'] = (cur.get('問題', '') + s).strip()
                    cur['_last'] = '問題'
                continue
        if cur:
            items.append(cur)
    for it in items:
        it.pop('_last', None)
    return items

def main():
    os.makedirs(OUT, exist_ok=True)
    labels, codes = build_segidx()
    cur = build_cur()
    items = parse_resp()
    json.dump({'labels': labels, 'codes': codes}, open(os.path.join(OUT, 'segidx.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(cur, open(os.path.join(OUT, 'cur.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(items, open(os.path.join(OUT, 'items_raw.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('labels', len(labels), 'codes', len(codes), 'cur blocks', len(cur), 'items', len(items))
    find = [i for i in items if i['section'] == 'find']
    doubt = [i for i in items if i['section'] == 'doubt']
    print('find', len(find), 'doubt', len(doubt))
    # resolution stats
    ok = 0; nocur = 0; nolabel = 0
    for it in find:
        lab = it['label']
        if lab not in cur:
            nocur += 1
        else:
            ok += 1
    print('find items with resolvable current text:', ok, 'unresolved:', nocur)
    import collections
    print('pl', collections.Counter(i['pl'] for i in find))
    print('conf', collections.Counter(i.get('信心', '')[:2] for i in find))

if __name__ == '__main__':
    main()
