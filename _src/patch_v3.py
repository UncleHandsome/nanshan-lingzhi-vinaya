
import io, os
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\user'
reps = {
 'p1.md': [
  ("佛法的住持與弘傳，使眾多經論的諍辯因戒行而得以止息。",
   "佛法的住持與弘傳，使一切經論在此都退讓高唱，唯推戒律為最勝根本。"),
  ("後人照著文字去操作，往往辨不清前後次第；",
   "後人照著文字去操作，往往辨不清這羯磨到底該用在什麼事上；"),
 ],
 'p2.md': [
  ("其餘若有本律文字未明了、事情在廢立之前；",
   "其餘若有本律文字未明了、該事屬於後期經教廢止之前者；"),
  ("其結罪位列於律典第五篇（突吉羅），在諸位大僧戒末。",
   "其結罪位列於律典第五篇（突吉羅），在罪名品位上列於一切戒條之最末。"),
 ],
 'p3.md': [
  ("如同漉水救蟲的比喻。",
   "如同兩位比丘在荒漠中寧死不飲蟲水、以命護戒的比喻。"),
 ],
 'p4.md': [
  ("答：各家說法不一，如今的正解是：",
   "答：各家說法不一，若依本宗破除舊說的決定之解："),
 ],
}
ok = True
for fn, pairs in reps.items():
    p = os.path.join(base, fn)
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        c = s.count(old)
        if c != 1:
            print('MISS', fn, c, old[:24]); ok = False; continue
        s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)

# builder: strip ** in headings, drop cover note, extend fix list
bp = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\build_user.py'
s = io.open(bp, encoding='utf-8').read()
s = s.replace("    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER\n    set_run(p.add_run('語譯依讀者指定之版本排印'), 9, color=RGBColor(0x99, 0x99, 0x99))\n", "")
s = s.replace("            set_run(p.add_run(b['text']), 13, bold=True, color=RGBColor(0, 0, 0))",
              "            set_run(p.add_run(b['text'].strip('*')), 13, bold=True, color=RGBColor(0, 0, 0))")
s = s.replace("            set_run(p.add_run(b['text']), 11.5, bold=True, color=RGBColor(0, 0, 0))",
              "            set_run(p.add_run(b['text'].strip('*')), 11.5, bold=True, color=RGBColor(0, 0, 0))")
s = s.replace("        ('合角量', '前作「折算拉平」。今改「合角量取」，即量其對角，最多三由旬。'),",
              """        ('合角量', '前作「折算拉平」。今改「合角量取」，即量其對角，最多三由旬。'),
        ('群籍息唱', '前作「平息經論諍辯」。今改：一切經論在此退讓高唱，唯推戒律為最勝。'),
        ('不辨前事', '前作「辨不清前後次第」。今改：辨不清這羯磨該用在什麼事上。'),
        ('如飲水殺蟲', '前作「漉水救蟲」。今還原為二比丘荒漠寧死不飲蟲水、以命護戒之喻。'),
        ('事在廢前', '前作「事情在廢立之前」。今改：該事屬後期經教廢止之前者。'),
        ('就位在諸戒末', '前作「在諸位大僧戒末」。今改：在罪名品位上列於一切戒條之最末。'),
        ('自然正解', '第二答補明「若依本宗破除舊說之決定之解」，理順六十三步與三十一步半。'),""")
io.open(bp, 'w', encoding='utf-8').write(s)
print('done', ok)
