# -*- coding: utf-8 -*-
"""把六書 Word／PDF 上傳到 GitHub Releases，並產生下載頁需要的清單。

需要 GitHub token（classic 或 fine-grained，需 repo 權限）：
  $env:GH_TOKEN='ghp_xxx'
  python -X utf8 _src/make_release.py

行為：
  1. 讀 git remote 取得 owner/repo
  2. 標籤預設 books-<日期>-<commit 短碼>
  3. 建立（或重用）release，逐檔上傳（已存在同名資產則跳過）
  4. 寫 docs/download_manifest.json：tag、commit、產生時間、每檔的 release 下載網址

不上傳任何檔案到 repo；PDF／Word 只存在 release 資產中。
"""
import glob
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DOCS = os.path.join(B, 'docs')
MANIFEST = os.path.join(DOCS, 'download_manifest.json')
DIRS = [
    ('白話對照本_標楷_單欄_DOCX', 'docx', '單欄'),
    ('白話對照本_標楷_單欄_PDF', 'pdf', '單欄'),
    ('白話對照本_標楷_雙欄_DOCX', 'docx', '雙欄'),
    ('白話對照本_標楷_雙欄_PDF', 'pdf', '雙欄'),
]
API = 'https://api.github.com'



VOL_ASCII = {'卷首': 'shou', '卷上': 'shang', '卷中': 'zhong', '卷下': 'xia',
             '卷一': '01', '卷二': '02', '卷三': '03', '卷四': '04',
             '卷五': '05', '卷六': '06'}
BOOK_MATCH = [('資持記', 'zhichi'), ('含注戒本疏', 'jieshu'), ('刪繁補闕行事鈔', 'xingshichao'),
              ('羯磨疏', 'yeshu'), ('拾毗尼義鈔', 'yichao'), ('比丘尼鈔', 'nicao'),
              ('行事鈔', 'xingshichao'), ('戒疏', 'jieshu'), ('業疏', 'yeshu'),
              ('尼鈔', 'nicao'), ('義鈔', 'yichao')]


def ascii_name(fn):
    """四分律刪繁補闕行事鈔_卷上_白話對照本_單欄.pdf → xingshichao-shang-single.pdf"""
    import re as _re
    book = ''
    for k, v in BOOK_MATCH:
        if k in fn:
            book = v
            break
    m = _re.search(r'_(卷[首上中下一二三四五六])_白話對照本', fn)
    vol = m.group(1) if m else ''
    layout = 'double' if '雙欄' in fn else 'single'
    ext = 'pdf' if fn.lower().endswith('.pdf') else 'docx'
    return '%s-%s-%s.%s' % (book or 'book', VOL_ASCII.get(vol, 'vol'), layout, ext)

def git(*args):
    return subprocess.run(['git'] + list(args), cwd=B, capture_output=True, text=True).stdout.strip()


def repo_slug():
    url = git('remote', 'get-url', 'origin')
    m = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', url)
    if not m:
        raise SystemExit('無法從 remote 取得 repo：%s' % url)
    return m.group(1), m.group(2)


def req(method, url, token, data=None, ctype='application/json'):
    body = None
    if data is not None:
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
    r = urllib.request.Request(url, data=body, method=method,
                               headers={'Authorization': 'token ' + token,
                                        'Accept': 'application/vnd.github+json',
                                        'Content-Type': ctype,
                                        'User-Agent': 'nanshan-release'})
    try:
        with urllib.request.urlopen(r, timeout=600) as resp:
            return json.loads(resp.read().decode('utf-8') or '{}')
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', errors='replace')[:400]
        raise SystemExit('HTTP %s %s %s\n%s' % (e.code, method, url, detail))


def load_token():
    """優先讀環境變數，其次讀本機 .gh_token（已列入 .gitignore，不會進版控）。"""
    t = (os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or '').strip()
    if t:
        return t
    for name in ('.gh_token', '.github_token'):
        p = os.path.join(B, name)
        if os.path.exists(p):
            return io.open(p, encoding='utf-8').read().strip()
    return ''


def main():
    token = load_token()
    if not token:
        raise SystemExit('找不到 GitHub token：請設 GH_TOKEN，或把 token 放進 .gh_token')
    owner, repo = repo_slug()
    commit = git('rev-parse', '--short', 'HEAD')
    tag = os.environ.get('REL_TAG') or ('books-%s-%s' % (time.strftime('%Y%m%d'), commit))
    name = '六書白話對照本 %s（定稿 %s）' % (time.strftime('%Y-%m-%d'), commit)
    print('repo=%s/%s tag=%s' % (owner, repo, tag))

    rel = None
    try:
        rel = req('GET', '%s/repos/%s/%s/releases/tags/%s' % (API, owner, repo, tag), token)
        print('沿用既有 release id=%s' % rel['id'])
    except SystemExit:
        rel = req('POST', '%s/repos/%s/%s/releases' % (API, owner, repo), token,
                  {'tag_name': tag, 'name': name,
                   'body': '六書白話對照本（標楷體 14pt）。定稿 commit `%s`，產生於 %s。'
                           % (commit, time.strftime('%Y-%m-%d %H:%M')),
                   'draft': False, 'prerelease': False})
        print('建立 release id=%s' % rel['id'])

    have = {a['name'] for a in rel.get('assets', [])}
    files = []
    for d, kind, layout in DIRS:
        for p in sorted(glob.glob(os.path.join(B, d, '*'))):
            if not os.path.isfile(p):
                continue
            fn = os.path.basename(p)
            files.append((p, fn, kind, layout))
    print('待上傳 %d 檔' % len(files))

    out = []
    for p, fn, kind, layout in files:
        aname = ascii_name(fn)
        if aname not in have:
            aname = ascii_name(fn)
            url = ('https://uploads.github.com/repos/%s/%s/releases/%s/assets?name=%s'
                   % (owner, repo, rel['id'], urllib.parse.quote(aname)))
            with io.open(p, 'rb') as fh:
                data = fh.read()
            up = req('POST', url, token, data,
                     ctype='application/octet-stream')
            have.add(aname)
            print('上傳', fn, '→', aname, up.get('state'))
        else:
            print('已存在，跳過', fn)
        out.append({'name': fn, 'asset': aname, 'kind': kind, 'layout': layout,
                    'size': os.path.getsize(p),
                    'url': 'https://github.com/%s/%s/releases/download/%s/%s'
                           % (owner, repo, tag, urllib.parse.quote(aname))})

    man = {'tag': tag, 'commit': commit, 'generated': time.strftime('%Y-%m-%d %H:%M'),
           'release_url': rel.get('html_url', ''),
           'files': out}
    io.open(MANIFEST, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(man, ensure_ascii=False, indent=1) + '\n')
    print('已寫 %s（%d 檔）' % (os.path.basename(MANIFEST), len(out)))


if __name__ == '__main__':
    main()
