# -*- coding: utf-8 -*-
"""增量建置：只重建「來源有變」的書與 PDF。

用法：
    python _src/build_dirty.py            # 檢查並重建
    python _src/build_dirty.py --status   # 只看狀態

狀態檔：AI語譯/_work/build_state.json
"""
import os, io, re, sys, glob, json, hashlib, subprocess

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PY = sys.executable
STATE = os.path.join(B, 'AI語譯', '_work', 'build_state.json')


def dir_hash(paths):
    h = hashlib.md5()
    for d in paths:
        for f in sorted(glob.glob(os.path.join(d, '**', '*.txt'), recursive=True)):
            h.update(os.path.basename(f).encode())
            h.update(io.open(f, 'rb').read())
    return h.hexdigest()


def run(args, label):
    print('>>', label, flush=True)
    r = subprocess.run([PY, '-X', 'utf8'] + args, cwd=B, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    ok = r.returncode == 0
    out = (r.stdout or '').strip().split('\n')[-2:]
    print('\n'.join(out), flush=True)
    if not ok:
        print('!! FAIL', label, (r.stderr or '')[-400:], flush=True)
    return ok


def main():
    status_only = '--status' in sys.argv
    st = {'books': {}, 'appendix': ''}
    if os.path.exists(STATE):
        st = json.load(io.open(STATE, encoding='utf-8'))

    books = {
        '01_行事鈔': [os.path.join(B, 'AI語譯', 'out', '01_行事鈔')],
        '資持記': [os.path.join(B, 'AI語譯', 'out', '資持記')],
        '02_戒疏': [os.path.join(B, 'AI語譯', 'out', '02_戒疏')],
        '03_業疏': [os.path.join(B, 'AI語譯', 'out', '03_業疏'), os.path.join(B, 'TXT_分卷_標點', '03_業疏'), os.path.join(B, 'AI語譯', '_work')],
        '04_比丘尼鈔': [os.path.join(B, 'AI語譯', 'out', '04_比丘尼鈔')],
        '05_拾毗尼義鈔': [os.path.join(B, 'AI語譯', 'out', '05_拾毗尼義鈔')],
    }
    dirty = []
    for name, paths in books.items():
        h = dir_hash(paths)
        old = st['books'].get(name, '')
        changed = (h != old)
        print('%-10s %s' % (name, '變動' if changed else '未變'), flush=True)
        if changed:
            dirty.append(name)
            st['books'][name] = h

    if status_only:
        return 0
    if not dirty:
        print('沒有變動，略過建置')
        return 0

    ok = True
    if '01_行事鈔' in dirty or '資持記' in dirty:
        ok &= run(['_src/mk_pian_split.py'] + [str(i) for i in range(1, 31) if i != 6], '會本 30 篇')
        ok &= run(['_src/build_vol.py'], '行事鈔三卷')
        ok &= run(['_src/rebuild_hebian_v2.py'], '合編 docx')
        ok &= run(['_src/site_hebian.py'], '合編網站')
    if '資持記' in dirty:
        ok &= run(['_src/build_book.py', '資持記', '四分律行事鈔資持記', '資持記', '資持記_細分'], '資持記十六卷')
    if '02_戒疏' in dirty:
        ok &= run(['_src/build_book.py', '02_戒疏', '四分律含注戒本疏', '戒疏', '02_戒疏'], '戒疏八卷')
    if {'03_業疏', '04_比丘尼鈔', '05_拾毗尼義鈔'} & set(dirty):
        ok &= run(['_src/build_ju_vol.py', '--no-pdf'], '業疏/尼鈔/義鈔 docx')
    ok &= run(['_src/site2.py'], '全站')
    ok &= run(['_src/mk_pdfs.py', '--jobs', '4'], 'PDF（只轉過期的）')

    if ok:
        json.dump(st, io.open(STATE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('已更新狀態檔')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
