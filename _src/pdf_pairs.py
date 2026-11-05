# -*- coding: utf-8 -*-
"""從《業疏_句讀對照本》PDF 取回「句讀原文↔白話」對照。

PDF 由 build_reflow.py 產生：原文＝褐色(#5f4e3c)、譯文＝黑色(#000000)、
頁眉頁腳＝灰色。以 pdftohtml -xml 取得每個字的座標與字體，重組段落。
"""
import os, io, re, sys, json, subprocess, html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PDF = os.path.join(B, '白話', '對照本', '業疏_句讀對照本.pdf')
XML = os.path.join(B, '_build', 'ys_pdf.xml')
OUT = os.path.join(B, 'AI語譯', '_work', 'ys_ju_pairs.json')

SRC_COLORS = {'5f4e3c'}
TR_COLORS = {'000000'}


def build_xml():
    if os.path.exists(XML) and os.path.getsize(XML) > 1000000:
        return
    print('extracting pdf -> xml ...')
    with io.open(XML, 'w', encoding='utf-8') as fh:
        subprocess.run(['pdftohtml', '-xml', '-stdout', PDF], stdout=fh, stderr=subprocess.DEVNULL)
    print('xml bytes', os.path.getsize(XML))


def main():
    build_xml()
    txt = io.open(XML, encoding='utf-8').read()
    fonts = {}
    for m in re.finditer(r'<fontspec id="(\d+)"[^>]*size="([\d.]+)"[^>]*color="#([0-9a-fA-F]{6})"', txt):
        fonts[m.group(1)] = (float(m.group(2)), m.group(3).lower())

    pages = re.split(r'<page [^>]*>', txt)[1:]
    paras = []          # list of dict(color, text)
    for page in pages:
        items = []
        for m in re.finditer(r'<text top="(-?\d+)" left="(-?\d+)"[^>]*font="(\d+)"[^>]*>(.*?)</text>', page):
            top, left, fid, t = int(m.group(1)), int(m.group(2)), m.group(3), html.unescape(m.group(4))
            size, color = fonts.get(fid, (0.0, ''))
            if size < 12:
                continue
            items.append((top, left, color, t))
        if not items:
            continue
        items.sort()
        lines = []
        for top, left, color, t in items:
            if lines and abs(lines[-1][0] - top) <= 3:
                lines[-1][1].append((left, t))
                lines[-1][2].append(color)
            else:
                lines.append([top, [(left, t)], [color]])
        # page-local paragraphs
        local = []
        for top, parts, colors in lines:
            parts.sort()
            buf = []
            prev = None
            for left, t in parts:
                if prev is not None and left - prev > 6:
                    buf.append(' ')
                buf.append(t)
                prev = left
            s = ''.join(buf).strip()
            if not s:
                continue
            col = max(set(colors), key=colors.count)
            if local and local[-1]['color'] == col and top - local[-1]['top'] <= 26:
                local[-1]['text'] += s
                local[-1]['top'] = top
            else:
                local.append(dict(color=col, text=s, top=top))
        # merge with previous page continuation
        for p in local:
            pcls = 'src' if p['color'] in SRC_COLORS else ('tr' if p['color'] in TR_COLORS else 'other')
            if paras and paras[-1]['cls'] == pcls and pcls != 'other' and p['top'] < 120:
                paras[-1]['text'] += p['text']
            else:
                paras.append(dict(cls=pcls, text=p['text']))

    print('paragraphs', len(paras))
    pairs = []
    pending = None
    for p in paras:
        if p['cls'] == 'src':
            pending = p['text']
        elif p['cls'] == 'tr' and pending:
            pairs.append((pending, p['text']))
            pending = None
    print('pairs', len(pairs))
    json.dump(pairs, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('saved', OUT)
    for o, t in pairs[:3]:
        print('O:', o[:50])
        print('T:', t[:50])


if __name__ == '__main__':
    main()
