# -*- coding: utf-8 -*-
"""再審指南實作回歸測試（不跑 qwen、不讀寫 定稿）。

跑法：
  python -X utf8 _src/test_reaudit_guides.py
"""
import io
import os
import sys
import unittest

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))

import book_config as BC      # noqa: E402
import materials_io as MI     # noqa: E402
import norm as NM             # noqa: E402
import recheck_scan as RC     # noqa: E402

CASE_WORDS = ('中國', '人語', '通解', '不作餘食法', '八遮', '下手疏', '刮刀', '波羅夷',
              '房舍田園', '目連', '周禮', '眼暗', '六局', '生貧', '六七百年',
              '齊魯二變', '韋編三絕', '得在浮沈', '隱顯互見', '執情三品', '背別')


class TestDeOverfit(unittest.TestCase):
    def test_prompts_have_no_case_words(self):
        for name in ('REAUDIT_PROMPT', 'REAUDIT_PACK_PROMPT', 'REVISE_PROMPT',
                     'VERIFY_PROMPT', 'SUBSTANTIVE_STYLE', 'NICAO_NOTE',
                     'CHOU_NOTE', 'YICHAO_NOTE', 'SHUJI_NOTE_YS', 'SHUJI_NOTE_JX',
                     'JI_NOTE', 'DUAL_NOTE', 'PREFACE_NOTE', 'DANGLING_NOTE',
                     'TYPO_NOTE'):
            t = getattr(BC, name)
            hit = [w for w in CASE_WORDS if w in t]
            self.assertFalse(hit, '%s 仍含抽樣詞例：%s' % (name, hit))

    def test_case_words_live_only_in_scanner(self):
        self.assertIn('FALSE_FRIEND', dir(RC))
        self.assertTrue(any(w == '中國' for w in RC.FALSE_FRIEND))
        self.assertTrue(any('波羅夷' in RC.BOOK_TERMS.get('尼鈔', ()) for _ in (0,)))

    def test_no_unfilled_placeholders(self):
        for name in ('REAUDIT_PROMPT', 'REVISE_PROMPT', 'VERIFY_PROMPT'):
            left = BC.leftovers(getattr(BC, name))
            self.assertEqual(left, ['{book_note}'], name)
        p = BC.reaudit_prompt('義鈔', labs=['鈔文'], src='此律云。', out='本律說：')
        self.assertEqual(BC.leftovers(p), [])
        p = BC.verify_prompt('尼鈔')
        self.assertEqual(BC.leftovers(p), [])

    def test_dynamic_notes(self):
        n = BC.notes_for('業疏', ['疏文', '記文'], '文云…', '譯文', key='01a_卷一之一_0001')
        self.assertIn('雙向互核', n['dual_note'])
        n = BC.notes_for('戒疏', ['疏文'], '序曰：夫…', '譯文', key='00_卷首_0011')
        self.assertIn('序跋', n['preface_note'])
        self.assertIn('江戶', n['pref_era'])
        n = BC.notes_for('尼鈔', ['鈔文'], '若人犯重云。', '譯文', key='10')
        self.assertIn('句末引導詞', n['dangling_note'])
        n = BC.notes_for('戒疏', ['疏文'], '眼暗未〔求〕時', '譯文', key='x')
        self.assertIn('疑似訛字', n['typo_note'])
        n = BC.notes_for('業疏', ['疏文'], '（本段前文）云云', '譯文', long=True, key='x')
        self.assertIn('長段切片', n['long_note'])

    def test_verify_effort_high(self):
        self.assertEqual(BC.STAGE_ENV['VERIFY']['QWEN_EFFORT'], 'high')
        self.assertEqual(BC.VERIFY_EFFORT, 'high')

    def test_book_of_prefers_excerpt(self):
        self.assertEqual(BC.book_of('（出處：《四分律刪補隨機羯磨疏》卷第一）'), '業疏')
        self.assertEqual(BC.book_of('（出處：《四分律含注戒本疏》卷第一）'), '戒疏')
        self.assertEqual(BC.book_of('（出處：《四分律刪繁補闕行事鈔資持記》）'), '資持記')
        self.assertEqual(BC.book_of('（出處：《四分律拾毗尼義鈔》卷上）'), '義鈔')
        self.assertEqual(BC.book_of('（出處：《四分律比丘尼鈔》卷上）'), '尼鈔')

    def test_render_audit_fills_dual_long(self):
        import mk_audit_materials as MA
        p = MA.render_audit('NOTE', 'DUAL', 'LONG')
        for ph in ('{book_note}', '{dual_note}', '{long_note}', '{logic_checklist}'):
            self.assertNotIn(ph, p)
        self.assertIn('DUAL', p)
        self.assertIn('LONG', p)
        self.assertIn('合理顯義', p)


class TestVerifyVerdict(unittest.TestCase):
    def test_ok_retry(self):
        self.assertEqual(MI.verify_verdict('【結論】\nOK\n【未過原因】無'), 'OK')
        self.assertEqual(MI.verify_verdict('【結論】\n`RETRY`\n【未過原因】漏改'), 'RETRY')
        self.assertEqual(MI.verify_verdict('【結論】\n不 OK，應 RETRY'), 'RETRY')
        self.assertEqual(MI.verify_verdict(''), 'ERROR')

    def test_reasons(self):
        self.assertEqual(MI.verify_reasons('【結論】\nOK\n【未過原因】無'), '')
        self.assertIn('漏改', MI.verify_reasons('【結論】\nRETRY\n【未過原因】\n漏改第二句'))

    def test_negative_pass_with_yu(self):
        self.assertEqual(MI.verdict('【結論】\n不應予 PASS，應判 FIX'), 'FIX')
        self.assertEqual(MI.verdict('【結論】\n勿判 PASS\n【必改硬傷】\n漏譯'), 'FIX')
        self.assertEqual(MI.verdict('【結論】\nPASS\n【必改硬傷】\n無'), 'PASS')


class TestNormLabeled(unittest.TestCase):
    def test_dual_column_own_source(self):
        # 記文 src 用「母論」→ 記文欄須還原《母論》；疏文 src 用「毘尼母」→ 不得被記文規則影響
        txt = ('【疏文】\n《毘尼母經》說：剃髮。\n\n'
               '【記文】\n《毘尼母經》說：剃髮。')
        out = NM.normalize_labeled(txt, {'疏文': '毘尼母云剃髮。',
                                         '記文': '母論云剃髮。'})
        a, b = out.split('【記文】')
        self.assertIn('《毘尼母經》', a)
        self.assertIn('《母論》', b)

    def test_bg_cut(self):
        out = NM.normalize('正文一句。\n\n【前文背景（僅供參考）】\n背景云云')
        self.assertNotIn('背景云云', out)
        self.assertIn('正文一句', out)

    def test_quote_var_map(self):
        # 白話引號內非原文逐字引用：却→卻；原文引詞（src 有兩字以上者）保留
        out = NM.normalize('他說「却說如此」，又引「却說」二字。', '「却說」二字')
        self.assertIn('「卻說如此」', out)
        self.assertIn('「却說」', out)

    def test_lone_corner(self):
        self.assertIn('「甲」', NM.normalize('『甲』'))

    def test_ci_lv_to_sifen(self):
        out = NM.normalize('【鈔文】此律云：犯重。本律學處。', '此律云犯重。')
        self.assertIn('《四分律》云', out)
        self.assertIn('本律學', out)


class TestRecheckFlags(unittest.TestCase):
    def _row(self, **kw):
        d = {'key': '01', 'label': '鈔文', 'source': '若人犯重。', 'translation': '【鈔文】若人犯重。'}
        d.update(kw)
        return d

    def _flags(self, **kw):
        return RC.scan_row('尼鈔', self._row(**kw))['flags']

    def test_empty_and_fields(self):
        self.assertIn('EMPTY_TR', self._flags(translation=''))
        self.assertIn('MISSING_FIELD', self._flags(translation=None))

    def test_src_boundary(self):
        self.assertIn('SRC_HEAD_CLOSE', self._flags(source='」者，若人犯重。'))
        self.assertIn('SRC_TAIL_NO_END', self._flags(
            source='若人犯重而無所畏懼故不得受用此物者應知如是'))
        self.assertNotIn('SRC_TAIL_NO_END', self._flags(source='若人犯重。'))

    def test_label_bg_gap(self):
        self.assertIn('NO_LEAD_LABEL', self._flags(translation='若人犯重。'))
        self.assertIn('BG_LEAK', self._flags(translation='【鈔文】若人犯重。\n【前文背景（僅供參考）】'))
        self.assertIn('GAP_SEG', self._flags(key='YE-G03'))

    def test_third_person_and_bad_var(self):
        self.assertIn('THIRD_PERSON', self._flags(translation='【鈔文】道宣說：若人犯重。'))
        self.assertNotIn('THIRD_PERSON', self._flags(source='道宣云若人犯重。',
                                                     translation='【鈔文】道宣說：若人犯重。'))
        self.assertIn('BAD_VAR_QUOTE', self._flags(translation='【鈔文】他說「却說」。'))
        self.assertNotIn('BAD_VAR_QUOTE', self._flags(source='「却」字云。',
                                                      translation='【鈔文】引「却」字。'))

    def test_bracket_tail_deng(self):
        self.assertIn('BRACKET_OVERFLOW', self._flags(translation='【鈔文】〔按：缺〕若人犯重。'))
        self.assertIn('TAIL_COLON', self._flags(translation='【鈔文】若人犯重：'))
        self.assertIn('DE_DENG', self._flags(translation='【鈔文】可以給小塊的等。'))
        self.assertIn('Q_WENDENG', self._flags(translation='【鈔文】如此嗎？等等。'))

    def test_ratio_and_corner(self):
        self.assertIn('INFLATE', self._flags(
            source='若人犯重而無所畏懼故應知如是。',
            translation='【鈔文】' + '這是很多很多的白話說明。' * 3))
        self.assertIn('SHRINK', self._flags(source='若人犯重而無所畏懼故不得受用此物者應知。' * 4,
                                            translation='【鈔文】犯重。'))
        self.assertIn('LONE_CORNER', self._flags(translation='【鈔文】『甲』'))

    def test_false_friend_and_book_term(self):
        f = self._flags(source='此律云中國人語。')
        self.assertIn('FALSE_FRIEND_HIT', f)
        f = self._flags(source='若比丘尼有刮刀削垢者。')
        self.assertIn('BOOK_TERM_HIT', f)


class TestVerifyClosedLoop(unittest.TestCase):
    def setUp(self):
        import verify_reaudit as VR
        self.VR = VR

    def test_changed_and_ratio(self):
        before = [{'lab': '鈔文', 'tr': '甲' * 10}]
        same = [{'lab': '鈔文', 'tr': '甲' * 10}]
        diff = [{'lab': '鈔文', 'tr': '乙' * 12}]
        self.assertEqual(self.VR._changed_parts(before, same), [])
        self.assertEqual(self.VR._changed_parts(before, diff), ['鈔文'])
        self.assertAlmostEqual(self.VR._ratio(before, diff), 1.2)

    def test_retry_material_merges_reasons(self):
        orig = ('舊提示\n\n---\n\n（出處：《尼鈔》卷上，10）\n\n【原文】\n■ 鈔文（原文）\n'
                '若人犯重。\n\n【目前譯文】\n【鈔文】\n舊譯。\n\n【必改硬傷】\n- 舊硬傷\n')
        merged = self.VR._merge_fixes('- 舊硬傷', '第二句漏改')
        self.assertIn('上一次 VERIFY 未過原因', merged)
        out = self.VR._build_retry_material(
            orig, '【鈔文】\n新譯。', merged, '第二句漏改', book='尼鈔', key='10',
            parts=[{'lab': '鈔文', 'orig': '若人犯重。', 'tr': '若人犯重。'}])
        self.assertIn('新譯。', out)
        self.assertNotIn('舊譯。', out)
        self.assertIn('舊硬傷', out)
        self.assertIn('第二句漏改', out)
        self.assertIn('你是南山律典定點修訂編輯', out)
        self.assertNotIn('舊提示', out)
        self.assertIn('比丘尼鈔', out)

    def test_verify_material_blocks(self):
        parts = [{'lab': '鈔文', 'orig': '若人犯重。', 'tr': '若人犯重。'}]
        md = self.VR._verify_material('尼鈔', '10', parts, '- 漏譯', '舊譯', '新譯')
        for blk in ('【原文】', '【硬傷清單】', '【修訂前譯文】', '【修訂後譯文】'):
            self.assertIn(blk, md)
        self.assertIn('RETRY', md)
        self.assertIn('正當維持原譯', md)


class TestStaticWiring(unittest.TestCase):
    def test_build_a2_pending_verify(self):
        t = io.open(os.path.join(B, '_src', 'build_a2.py'), encoding='utf-8').read()
        self.assertIn('_待驗收清單.txt', t)
        self.assertIn('normalize_labeled', t)

    def test_verify_reaudit_effort(self):
        t = io.open(os.path.join(B, '_src', 'verify_reaudit.py'), encoding='utf-8').read()
        self.assertIn("BC.STAGE_ENV.get('VERIFY'", t)
        self.assertIn('_人工複核清單.txt', t)

    def test_final_merge_seven_items(self):
        t = io.open(os.path.join(B, '_src', 'check_final_merge.py'), encoding='utf-8').read()
        for item in ('source == raw', '未定位', '區間重疊', '空白譯文／缺欄',
                     '缺開頭標籤／背景外洩', '缺口段再審紀錄', '非正文如實排除'):
            self.assertIn(item, t)


if __name__ == '__main__':
    unittest.main(verbosity=2)
