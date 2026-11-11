# -*- coding: utf-8 -*-
"""Clean parsed items: strip glued 存疑 tails, split doubts, normalise."""
import re, json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')

GLUE = re.compile(r'(?:\*\*\s*)?(?:【\s*)?存疑(?:（[^）]*）)?(?:\s*】)?(?:\*\*)?')
DOUBT_HDR = re.compile(r'存疑')

def clean():
    items = json.load(open(os.path.join(OUT, 'items_raw.json'), encoding='utf-8'))
    out = []
    extra = []
    for it in items:
        prob = it.get('問題', '') or ''
        m = GLUE.search(prob)
        if m and m.start() > 12 and re.search(r'\d{3}-\d{4}|#\d+', prob[m.start():]):
            tail = prob[m.start():]
            it['問題'] = prob[:m.start()].rstrip('，；、 ')
            it['_extra'] = tail
            extra.append({'file': it['file'], 'tail': tail})
        out.append(it)
    # reclassify pl 存疑 -> doubt
    for it in out:
        if it['section'] == 'find' and '存疑' in (it.get('pl') or ''):
            it['section'] = 'doubt'
            it['pl'] = '存疑'
        it['code'] = (it.get('code') or '').strip()
        it['label'] = (it.get('label') or '').strip()
    json.dump(out, open(os.path.join(OUT, 'items.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(extra, open(os.path.join(OUT, 'extra_doubt.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    find = [i for i in out if i['section'] == 'find']
    doubt = [i for i in out if i['section'] == 'doubt']
    print('items', len(out), 'find', len(find), 'doubt', len(doubt), 'extra', len(extra))
    import collections
    print(collections.Counter(i['pl'] for i in find))
    print(collections.Counter((i.get('信心') or '')[:1] for i in find))

if __name__ == '__main__':
    clean()
