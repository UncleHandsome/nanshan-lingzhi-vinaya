import io, os, re, glob, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out', '01_行事鈔')

PAIRS = [
    ('若善比丘置不訶責，當知是人佛法中怨', '如果持戒修善的善比丘放任不管而不加訶責，應當知道這個人是佛法中的怨敵；如果能夠驅遣、舉處並加以治罰，這才是我佛的弟子、真正的聲聞。'),
    ('自非治罰，何由可息？如似遲驢', '若非施以治罰，如何能夠止息惡行？就如同愚鈍遲緩的劣驢，必須施加楚罰鞭責；因此律中便有七種調伏之法，以及惡馬治、默擯、不與語等治罰。'),
    ('有過之徒，實當此罰；反用俗法', '有罪過之輩，確實應當受此治罰；然而近世反而採用世俗之法，不依佛理加以折伏；外相雖然看似調順，內心卻未曾悔改革新。以致使僧團的戒律聖網日益衰頹削弱。經文說：『非佛所制卻擅自制定，將會迅速毀滅正法。』這話確實切當。如今標舉經律中幽微深奧的教言，以重振像法時期的教運；有能力的住持與大眾執事，應當以此為準則遵照實行。'),
    ('具如律本遮法中說', '這一切都詳細記載在《四分律》本「遮犍度」中。如果違背上述法軌，舉發不知合於時宜，反而會引發鬥諍；所以經文說：『你們不要頻頻舉發他人的罪過，因為唯恐敗壞正法。』但如果已經具備上述如法的舉罪條件，卻放縱惡人而不加治罰，同樣也會毀滅正法。'),
]
files = os.listdir(OUT)
for needle, tr in PAIRS:
    hit = False
    for fn in files:
        fp = os.path.join(OUT, fn)
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
        for i, t in enumerate(tt):
            k = t.find(needle)
            if k > 0:
                tt[i] = t[:k] + tr
                io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
                print('補譯', fn, i + 1, needle[:8])
                hit = True
                break
        if hit:
            break
    if not hit:
        print('MISS', needle[:10])
