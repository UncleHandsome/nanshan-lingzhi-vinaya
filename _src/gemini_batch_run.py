# -*- coding: utf-8 -*-
"""上傳 JSONL 並建立 Gemini batch 作業。"""
import io
import json
import os
import sys
import time
import urllib.request
import urllib.error

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = io.open(os.path.join(B, '.gemini_key'), encoding='utf-8-sig').read().strip()
BASE = 'https://generativelanguage.googleapis.com'
MODEL = 'gemini-4-argon'
JL = os.path.join(B, 'AI語譯', '回譯測試', 'batch_input.jsonl')


def req(url, data=None, headers=None, method=None):
    h = {'Content-Type': 'application/json'}
    h.update(headers or {})
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    return urllib.request.urlopen(r, timeout=600)


def upload(path):
    size = os.path.getsize(path)
    # 1) start resumable upload
    start_req = urllib.request.Request(
        BASE + '/upload/v1beta/files?key=' + KEY,
        data=b'{}',
        headers={
            'X-Goog-Upload-Protocol': 'resumable',
            'X-Goog-Upload-Command': 'start',
            'X-Goog-Upload-Header-Content-Length': str(size),
            'X-Goog-Upload-Header-Content-Type': 'application/jsonl',
            'Content-Type': 'application/json',
        },
        method='POST')
    resp = urllib.request.urlopen(start_req, timeout=300)
    url = resp.headers.get('X-Goog-Upload-URL')
    if not url:
        raise RuntimeError('取不到 upload URL：' + str(resp.headers))
    # 2) upload bytes
    body = open(path, 'rb').read()
    up_req = urllib.request.Request(
        url, data=body,
        headers={'X-Goog-Upload-Offset': '0',
                 'X-Goog-Upload-Command': 'upload, finalize',
                 'Content-Length': str(size)},
        method='POST')
    out = json.loads(urllib.request.urlopen(up_req, timeout=600).read())
    return out['file']


def main():
    print('上傳', JL, os.path.getsize(JL), 'bytes')
    f = upload(JL)
    print('檔案上傳完成：', f.get('name'), f.get('state'))
    name = f['name']

    # 寫入記錄
    rec = os.path.join(B, 'AI語譯', '回譯測試', 'job.json')
    io.open(rec, 'w', encoding='utf-8').write(json.dumps({'file': name}, ensure_ascii=False))

    body = json.dumps({'batch': {'displayName': 'translation-argon-14',
                                'inputConfig': {'fileName': name}}}).encode()
    url = '%s/v1beta/models/%s:batchGenerateContent?key=%s' % (BASE, MODEL, KEY)
    try:
        r = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, data=body,
                                   headers={'Content-Type': 'application/json'}, method='POST'),
            timeout=600).read())
    except urllib.error.HTTPError as e:
        print('建立 batch 失敗：', e.code)
        print(e.read().decode()[:800])
        return
    print('batch 建立：', json.dumps(r, ensure_ascii=False)[:500])
    io.open(rec, 'w', encoding='utf-8').write(json.dumps({'file': name, 'batch': r}, ensure_ascii=False, indent=1))
    print('記錄寫入', rec)


if __name__ == '__main__':
    main()