import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('clear_output', ROOT / 'scripts/clear_output.py')
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def rules(report):
    return {item['rule'] for item in report['diagnostics']}


class ProseTests(unittest.TestCase):
    def test_chinese_is_counted_without_english_tokens(self):
        report = checker.check('构建完成。开始测试。通过后部署。', 'zh')
        self.assertEqual(report['metrics'], {'sentences_or_lines': 3, 'english_words': 0, 'han_characters': 13})
        self.assertEqual(report['coverage']['prose'], 'checked_heuristically')
        self.assertNotIn('score', report)

    def test_decimal_and_abbreviation_boundaries(self):
        report = checker.check('Dr. Smith waits 2.5 seconds. Then retry.', 'en')
        self.assertEqual(report['metrics']['sentences_or_lines'], 2)

    def test_language_is_explicit_and_quote_does_not_switch_it(self):
        report = checker.check('Explain the error "连接失败" in English. Check the connection.', 'en')
        self.assertEqual(report['language_profile'], 'en')
        self.assertNotIn('language.review', rules(report))
        self.assertEqual(report['metrics']['han_characters'], 0)
        with self.assertRaises(ValueError):
            checker.check('Hello.', 'auto')

    def test_obvious_language_mismatch_is_review_not_error(self):
        report = checker.check('构建完成后开始单元测试和安全扫描。', 'en')
        self.assertIn('language.review', rules(report))
        self.assertEqual(report['summary']['error'], 0)

    def test_mixed_prose_counts_both_languages(self):
        report = checker.check('检查 API，然后 retry the request。', 'mixed')
        self.assertGreater(report['metrics']['han_characters'], 0)
        self.assertGreater(report['metrics']['english_words'], 0)
        self.assertNotIn('language.review', rules(report))

    def test_chinese_and_english_length_are_independent_and_opt_in(self):
        text = '构建完成后开始单元测试和安全扫描。\nThe service sends a request to the server.'
        self.assertEqual(checker.check(text, 'mixed')['summary']['style'], 0)
        report = checker.check(text, 'mixed', max_en_words=5, max_zh_chars=8)
        self.assertEqual(rules(report), {'style.en_length', 'style.zh_length'})
        for limit in (0, -1, True):
            with self.assertRaises(ValueError):
                checker.check(text, 'mixed', max_en_words=limit)

    def test_offsets_survive_protected_content(self):
        text = '```js\nconst x = 1;\n```\n\n  The service sends a request to the server.'
        report = checker.check(text, 'en', max_en_words=5)
        self.assertEqual(report['diagnostics'][0]['location'], {'line': 5, 'column': 3})

    def test_varied_code_fences_and_unclosed_fence_are_protected(self):
        for fence, closing in [('```', '```'), ('~~~', '~~~'), ('````', '`````'), ('~~~', '')]:
            with self.subTest(fence=fence, closing=closing):
                text = fence + 'js\nconst should = "utilize";\n' + closing
                report = checker.check(text, 'en', max_en_words=1)
                self.assertEqual(report['status'], 'not_checked')
                self.assertEqual(report['summary']['style'], 0)
                self.assertEqual(report['coverage']['prose'], 'not_checked')

    def test_inline_code_quotes_links_and_url_do_not_trigger_terms(self):
        glossary = {'terms': [{'id': 'x', 'en': {'preferred': 'use', 'avoid': ['utilize']}}]}
        for text in ['`utilize()`', '``call(`utilize`)``', '> utilize\n', '    utilize\n',
                     '"utilize"', '“utilize”', '[guide](https://example.test/utilize)',
                     'https://example.test/utilize']:
            with self.subTest(text=text):
                self.assertNotIn('term.preference', rules(checker.check(text, 'en', glossary=glossary)))

    def test_text_after_chinese_url_punctuation_is_not_swallowed(self):
        report = checker.check('https://example.test，检查服务。', 'zh')
        self.assertEqual(report['metrics']['han_characters'], 4)

    def test_project_terms_do_not_rewrite_or_translate(self):
        glossary = checker.strict_json((ROOT / 'references/glossary.example.json').read_text(encoding='utf-8'))
        report = checker.check('A time-out occurred. 发生逾时。', 'mixed', glossary=glossary)
        self.assertEqual(report['summary']['style'], 2)
        self.assertEqual({i['preferred'] for i in report['diagnostics']}, {'timeout', '超时'})
        only_en = checker.check('A time-out occurred. 发生逾时。', 'en', glossary=glossary)
        self.assertEqual([i['preferred'] for i in only_en['diagnostics'] if i['rule'] == 'term.preference'], ['timeout'])

    def test_term_identifier_boundaries_and_phrase_exceptions(self):
        glossary = {'terms': [
            {'id': 'en', 'en': {'preferred': 'stop', 'avoid': ['terminate']}},
            {'id': 'zh', 'zh': {'preferred': '反馈', 'avoid': ['闭环'], 'except': ['闭环控制']}},
        ]}
        self.assertNotIn('term.preference', rules(checker.check('terminate_worker uses 闭环控制。', 'mixed', glossary=glossary)))
        self.assertIn('term.preference', rules(checker.check('terminate the worker.', 'en', glossary=glossary)))


class ContractTests(unittest.TestCase):
    def test_explicit_literal_even_in_protected_code(self):
        contract = {'required_literals': ["tool --dry-run --path './draft files'"]}
        correct = "Run `tool --dry-run --path './draft files'`."
        self.assertEqual(checker.check(correct, 'en', contract=contract)['summary']['error'], 0)
        self.assertIn('literal.missing', rules(checker.check(correct.replace('--dry-run', '--run'), 'en', contract=contract)))

    def test_authorized_command_edit_uses_new_contract(self):
        report = checker.check('Run `tool --run`.', 'en', source='Run `tool --dry-run`.',
                               contract={'required_literals': ['tool --run']})
        self.assertEqual(report['diagnostics'], [])

    def test_json_contract_accepts_valid_raw_object(self):
        contract = {'format': 'json', 'json_keys': ['observation', 'next_step'], 'required_literals': ['ECONNRESET']}
        report = checker.check('{"observation":"ECONNRESET", "next_step":"检查连接"}', 'zh', contract=contract)
        self.assertEqual(report['summary']['error'], 0)
        self.assertEqual(report['coverage']['prose'], 'not_checked')

    def test_json_rejects_fences_duplicate_keys_constants_and_wrong_keys(self):
        for text in ['```json\n{}\n```', '{"x":1,"x":2}', '{"x":NaN}', '{"x":1} trailing', '{"y":1}', '[]']:
            with self.subTest(text=text):
                report = checker.check(text, 'en', contract={'format': 'json', 'json_keys': ['x']})
                self.assertGreater(report['summary']['error'], 0)

    def test_json_source_comparison_is_explicitly_skipped(self):
        report = checker.check('{"x":2}', 'en', source='{"x":1}', contract={'format': 'json'})
        self.assertEqual(report['coverage']['source_comparison'], 'skipped_json')
        self.assertEqual(report['coverage']['semantic_equivalence'], 'not_verified')

    def test_empty_output_is_error(self):
        self.assertIn('format.empty', rules(checker.check(' \n', 'en')))

    def test_invalid_config_does_not_silently_disable_checks(self):
        for contract in [[], {'formats': 'json'}, {'format': 'html'}, {'required_literals': 'x'},
                         {'required_literals': ['']}, {'json_keys': ['x']}, {'json_keys': ['x', 'x'], 'format': 'json'}]:
            with self.subTest(contract=contract), self.assertRaises(ValueError):
                checker.check('Text.', 'en', contract=contract)
        for glossary in [[], {}, {'terms': ['x']}, {'terms': [{'id': 'x'}]},
                         {'terms': [{'id': 'x', 'en': {'preferred': '', 'avoid': ['x']}}]}]:
            with self.subTest(glossary=glossary), self.assertRaises(ValueError):
                checker.check('Text.', 'en', glossary=glossary)


class RewriteTests(unittest.TestCase):
    def test_english_possibility_change_needs_review(self):
        report = checker.check('The request will fail.', 'en', source='The request may fail.')
        self.assertIn('meaning.possibility', rules(report))
        self.assertEqual(report['summary']['error'], 0)

    def test_chinese_advice_approximation_and_permission_are_preserved(self):
        source = '建议先备份配置。等待约 5 秒后，可以重试；如果任务已取消，则不要重试。'
        faithful = '建议先备份配置。如果任务已取消，不要重试。否则，等待约 5 秒后，可以重试。'
        self.assertEqual(checker.check(faithful, 'zh', source=source)['diagnostics'], [])
        changed = '必须先备份配置。等待 5 秒后重试。'
        findings = rules(checker.check(changed, 'zh', source=source))
        self.assertTrue({'meaning.recommendation', 'meaning.obligation', 'meaning.approximation',
                         'meaning.permission_or_capability', 'meaning.negation', 'meaning.condition'} <= findings)

    def test_changed_quantity_and_storage_unit_need_review(self):
        for source, output in [('Wait 5 seconds.', 'Wait 10 seconds.'), ('使用 5 MB。', '使用 5 GB。'),
                               ('Retry 3 times.', 'Retry 4 times.')]:
            with self.subTest(source=source):
                self.assertIn('meaning.quantities', rules(checker.check(output, 'mixed', source=source)))

    def test_exact_time_unit_conversions_and_number_formatting_are_allowed(self):
        for source, output in [('Wait 5 seconds.', 'Wait 5000 ms.'), ('等待约5秒。', '等待约5000毫秒。'),
                               ('等待1分钟。', '等待60秒。'), ('Use 5.0 MB.', 'Use 5 MB.')]:
            with self.subTest(source=source):
                self.assertNotIn('meaning.quantities', rules(checker.check(output, 'mixed', source=source)))

    def test_changed_parallel_marker_needs_review(self):
        source = '构建完成后，单元测试和安全扫描并行进行。两者都通过才部署。'
        self.assertIn('meaning.concurrency', rules(checker.check('构建完成后，先进行单元测试，再进行安全扫描。两者都通过才部署。', 'zh', source=source)))

    def test_numbered_steps_and_emphasis_are_not_new_quantities(self):
        source = '建议先备份配置。等待约 5 秒后，可以重试。'
        output = '1. 建议先备份配置。\n2. 等待约 **5** 秒后，可以重试。'
        self.assertEqual(checker.check(output, 'zh', source=source)['diagnostics'], [])

    def test_grouping_and_unit_whitespace_preserve_quantities(self):
        for output in ['Wait 1,000 ms.', 'Wait **1** second.', 'Wait 1\nsecond.', 'Wait 1\u202fsecond.']:
            with self.subTest(output=output):
                self.assertNotIn('meaning.quantities', rules(checker.check(output, 'en', source='Wait 1 second.')))

    def test_long_decimal_values_do_not_round_away_a_change(self):
        report = checker.check('Use 1234567890123456789012345678902 bytes.', 'en',
                               source='Use 1234567890123456789012345678901 bytes.')
        self.assertIn('meaning.quantities', rules(report))

    def test_new_explanation_does_not_claim_source_comparison(self):
        report = checker.check('Wait about 5 seconds.', 'en')
        self.assertEqual(report['coverage']['source_comparison'], 'not_requested')
        self.assertFalse(any(rule.startswith('meaning.') for rule in rules(report)))

    def test_known_semantic_blind_spot_is_not_claimed_verified(self):
        report = checker.check('Deploy if either check passes.', 'en', source='Deploy only if both checks pass.')
        self.assertEqual(report['diagnostics'], [])
        self.assertEqual(report['coverage']['semantic_equivalence'], 'not_verified')

    def test_tables_participate_in_quantity_comparison_not_length(self):
        report = checker.check('| Delay | 10 s |', 'en', source='| Delay | 5 s |', max_en_words=1)
        self.assertIn('meaning.quantities', rules(report))
        self.assertNotIn('style.en_length', rules(report))


class CliTests(unittest.TestCase):
    def test_cli_exit_codes_and_read_only_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original, output, contract = root / 'original.txt', root / 'answer.txt', root / 'contract.json'
            original.write_text('The request may fail.', encoding='utf-8')
            output.write_text('The request will fail.', encoding='utf-8')
            contract.write_text('{"required_literals":["ECONNRESET"]}', encoding='utf-8')
            before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (original, output, contract)]
            command = [sys.executable, str(ROOT / 'scripts/clear_output.py'), str(output), '--lang', 'en', '--source', str(original)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command + ['--fail-on', 'review'], capture_output=True).returncode, 1)
            failed = subprocess.run(command + ['--contract', str(contract)], capture_output=True, text=True)
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(json.loads(failed.stdout)['status'], 'errors')
            self.assertEqual(subprocess.run(command + ['--max-en-words', '0'], capture_output=True).returncode, 2)
            self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in (original, output, contract)])

    def test_version_does_not_need_input_or_language(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/clear_output.py'), '--version'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), (ROOT / 'VERSION').read_text().strip())


if __name__ == '__main__':
    unittest.main()
