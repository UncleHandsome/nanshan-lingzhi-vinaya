# -*- coding: utf-8 -*-
"""最小回歸測試：2026-11-22 尼鈔十段與品管漏洞修正。

跑法：
  python -X utf8 _src/test_regressions.py
"""
import io
import os
import sys
import unittest

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))

import book_config as BC          # noqa: E402
import check_align as CA          # noqa: E402
import local_corpus as LC         # noqa: E402
import materials_io as MI         # noqa: E402
import mk_audit_materials as MA   # noqa: E402
import mk_split_blind as MS       # noqa: E402
import norm as NM                 # noqa: E402
import qc_scan as QC              # noqa: E402


class TestQcScan(unittest.TestCase):
    def test_lead_label(self):
        self.assertEqual(QC.check_lead_label('【鈔文】\n第五行法'), [])
        self.assertTrue(QC.check_lead_label('第五行法者'))
        self.assertTrue(QC.check_lead_label('【修訂譯文】\n第五行法'))
        self.assertTrue(QC.check_lead_label(''))

    def test_bracket_overflow(self):
        self.assertEqual(QC.check_bracket_overflow('原文', '【鈔文】\n譯文'), [])
        self.assertEqual(QC.check_bracket_overflow('〔一本作X〕', '【鈔文】\n（一本作X）'), [])
        self.assertTrue(QC.check_bracket_overflow('原文', '【鈔文】\n〔原文此處缺第四項〕'))

    def test_tail_colon(self):
        self.assertTrue(QC.check_tail_colon('【鈔文】\n作白說：'))
        self.assertTrue(QC.check_tail_colon('【鈔文】\n作白說:'))
        self.assertEqual(QC.check_tail_colon('【鈔文】\n作白說。'), [])
        self.assertEqual(QC.check_tail_colon('【鈔文】\n他說：「莫放逸。」'), [])


class TestNorm(unittest.TestCase):
    def test_abbr_restore(self):
        src = '母論云剃髮者。'
        self.assertIn('《母論》', NM.normalize('《毘尼母論》說：剃髮。', src))
        self.assertIn('《善生》', NM.normalize('《善生經》說：瞻病。', '善生云瞻病人'))
        self.assertIn('《五百問事》', NM.normalize('《五百問事經》說：不還者犯重。', '五百問事云'))
        self.assertIn('《見論》', NM.normalize('《善見律毗婆沙》說：中人。', '見論云中人'))
        self.assertIn('《見論》', NM.normalize('《善見論》說：中人。', '見論云中人'))
        self.assertIn('《婆論》', NM.normalize('《薩婆多論》說：污家。', '婆論云作種種惡業'))

    def test_depth_reset_per_paragraph(self):
        # 第一段「未閉合，第二段（空行後）仍須正常轉換異體字
        out = NM.normalize('「未閉合的說法\n\n第二段說爲着衆')
        self.assertIn('說為著眾', out)


class TestVerdict(unittest.TestCase):
    def test_negative_pass_then_fix(self):
        self.assertEqual(MI.verdict('【結論】\n不應 PASS，應判 FIX\n'), 'FIX')
        self.assertEqual(MI.verdict('【結論】\n不得判為 PASS，應改判 FIX\n'), 'FIX')
        self.assertEqual(MI.verdict('【結論】\nPASS\n'), 'PASS')
        self.assertEqual(MI.verdict('【結論】\nFIX\n【必改硬傷】\n- 漏譯\n'), 'FIX')

    def test_is_keep_a_bounded(self):
        self.assertTrue(MI.is_keep_a('PASS_A_KEEP_A'))
        self.assertTrue(MI.is_keep_a('沿用譯本甲之譯文'))
        long_note = '沿用譯本甲，因本段屬長文切片，前後語氣連貫，僅補主語一處，其餘照舊不改。'
        self.assertFalse(MI.is_keep_a(long_note))


class TestAuditPrompt(unittest.TestCase):
    def test_placeholders_filled(self):
        p = MA.render_audit('《尼鈔》note', 'DUAL', 'LONG')
        for ph in ('{book_note}', '{logic_checklist}', '{dual_note}', '{long_note}'):
            self.assertNotIn(ph, p)
        self.assertIn('DUAL', p)
        self.assertIn('LONG', p)
        self.assertIn('檢核通則', p)
        self.assertIn(BC.LOGIC_CHECKLIST.split('①')[1][:8], p)

    def test_pick_tag_negation(self):
        self.assertEqual(MA._pick_tag('某句｜裁決（甲優）：', '理由'), '甲')
        self.assertEqual(MA._pick_tag('某句｜裁決（非甲優，乙較穩）：', '理由'), '乙')
        self.assertEqual(MA._pick_tag('某句｜裁決（乙優）：', '理由'), '乙')
        self.assertEqual(MA._pick_tag('某句｜裁決（重修）：', '理由'), '重修')
        self.assertEqual(MA._pick_tag('某句｜裁決：', '甲優'), '甲')


class TestSplitBlind(unittest.TestCase):
    def test_punctuated_split(self):
        txt = '若人持戒，' * 60
        parts = MS.split_sentences(txt, 100)
        self.assertGreaterEqual(len(parts), 2)
        self.assertEqual(''.join(parts), txt)

    def test_unpunctuated_unsafe(self):
        # 全無標點也無句首虛字：不得硬劈
        txt = '天地玄黃宇宙洪荒' * 150
        with self.assertRaises(MS.UnsafeSplit):
            MS.split_sentences(txt, 200)

    def test_unpunctuated_soft_head(self):
        # 底本無標點：以「若」等句首虛字為界，不劈開字詞
        txt = '天地玄黃宇宙洪荒' * 10 + '若人持戒' * 40
        parts = MS.split_sentences(txt, 100)
        self.assertGreaterEqual(len(parts), 2)
        self.assertEqual(''.join(parts), txt)
        self.assertTrue(parts[1].startswith('若'))


class TestLocalCorpus(unittest.TestCase):
    def test_plain_variants(self):
        self.assertEqual(LC._plain('終被鶴林之後'), '終被鶴林之後')
        self.assertEqual(LC._plain('窯治七眾'), '窯冶七眾')
        self.assertEqual(LC._plain('柘鬬提奢'), '柘鬥提奢')
        self.assertEqual(LC._plain('籬柵不周'), '籬柵不周')

    def test_mother_priority_list(self):
        self.assertIn('四分律', LC.NICAO_MOTHER)
        self.assertIn('摩訶僧祇律', LC.NICAO_MOTHER)
        self.assertIn('五分律', LC.NICAO_MOTHER)
        self.assertIn('十誦律', LC.NICAO_MOTHER)
        self.assertIn('毘尼母經', LC.NICAO_MOTHER)


class TestAlignScore(unittest.TestCase):
    def test_orig_only_material(self):
        # 盲翻材料常無舊譯：原文 2-gram 仍須能給分
        R2 = CA.grams('若人持戒清淨', 2)
        R3 = CA.grams('若人持戒清淨', 3)
        pack = (CA.grams('若人持戒清淨', 2), set())
        self.assertGreater(CA._score(R2, R3, pack), 0.0)
        self.assertEqual(CA._score(R2, R3, (set(), set())), 0.0)


class TestStaticGuards(unittest.TestCase):
    def test_qwen_local_filter_before_truncate(self):
        p = os.path.join(B, '_src', 'qwen_local.py')
        t = io.open(p, encoding='utf-8').read()
        self.assertIn('_fetch = min(20', t)
        self.assertIn('NO_TOOLS_SYSTEM = NO_TOOLS_SYSTEM.rstrip()', t)
        self.assertIn('hits = hits[:int(rows)]', t)
        # 不得先截 rows 再過濾
        self.assertNotIn('_LC.find(query, work, rows', t)

    def test_build_a2_amplitude_blocks(self):
        t = io.open(os.path.join(B, '_src', 'build_a2.py'), encoding='utf-8').read()
        self.assertIn('over.append(', t)
        self.assertIn('or over:', t)
        self.assertIn("_未完成清單.log", t)


if __name__ == '__main__':
    unittest.main(verbosity=2)
