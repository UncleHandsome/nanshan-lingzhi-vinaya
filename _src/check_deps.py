import os, io, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
need = [
    ('_src/site2.py', 'site2'),
    ('_src/site_assets.py', 'site_assets'),
    ('_src/site.css', 'site.css source'),
    ('_src/search.js', 'search.js source'),
    ('_src/site_ju.py', 'site_ju'),
    ('_src/site_hebian.py', 'site_hebian'),
    ('_src/toc_rules.py', 'toc_rules'),
    ('_src/nav.js', 'nav.js'),
    ('_src/build_ju_vol.py', 'build_ju_vol'),
    ('_src/build_vol.py', 'build_vol'),
    ('_src/mk_pian_split.py', 'mk_pian_split'),
    ('_src/mk_p6_huiben.py', 'mk_p6_huiben'),
    ('_src/export_materials.py', 'export_materials'),
    ('_src/chk_11_30.py', 'chk_11_30'),
    ('_src/chk_pian_docs.py', 'chk_pian_docs'),
    ('_src/dedup_yeshu_docx.py', 'dedup_yeshu_docx'),
    ('docs/style.css', 'style.css'),
    ('docs/nav.js', 'docs/nav.js'),
    ('docs/search.js', 'docs/search.js'),
    ('docs/search/manifest.js', 'docs/search/manifest.js'),
    ('AI語譯/_work/hb_align.json', 'hb_align'),
    ('AI語譯/_work/hb_align_ys.json', 'hb_align_ys'),
    ('AI語譯/_work/ys_offsets_final.json', 'ys_offsets_final'),
    ('AI語譯/_work/ys_align_map.json', 'ys_align_map'),
    ('AI語譯/_work/ys_ju_map.json', 'ys_ju_map'),
    ('AI語譯/_work/yeshu_punct.json', 'yeshu_punct'),
    ('AI語譯/_work/yeshu_tags.json', 'yeshu_tags'),
    ('AI語譯/_work/nicao_punct.json', 'nicao_punct'),
    ('AI語譯/_work/yichao_punct.json', 'yichao_punct'),
    ('TXT_分卷/資持記_細分', 'dir 資持記_細分'),
    ('TXT_分卷/01_行事鈔', 'dir 01_行事鈔'),
    ('TXT_句讀/03_業疏', 'dir 句讀業疏'),
]
miss = []
for p, label in need:
    fp = os.path.join(B, p)
    ok = os.path.exists(fp)
    print(('OK  ' if ok else 'MISS'), label, p)
    if not ok:
        miss.append(p)
print('missing:', len(miss))
