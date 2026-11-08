import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.error import HTTPError, URLError
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


updater = load('check_update', 'scripts/check_update.py')
builder = load('build_release', 'tools/build_release.py')


class UpdateTests(unittest.TestCase):
    def test_numeric_version_comparison(self):
        self.assertEqual(updater.compare_release('0.9.0', {'tag_name': 'v0.10.0'})['status'], 'update_available')
        self.assertEqual(updater.compare_release('0.10.0', {'tag_name': 'v0.10.0'})['status'], 'same_version')
        self.assertEqual(updater.compare_release('0.11.0', {'tag_name': 'v0.10.0'})['status'], 'local_ahead')

    def test_unversioned_install_is_not_assumed_current(self):
        result = updater.compare_release(None, {'tag_name': 'v0.1.0'})
        self.assertEqual(result['status'], 'installed_version_unknown')
        self.assertFalse(result['updated_files'])

    def test_invalid_or_prerelease_metadata_is_rejected(self):
        for release in [[], {}, {'tag_name': 'v0.1.0', 'draft': True}, {'tag_name': 'v0.1.0', 'prerelease': True},
                        {'tag_name': 'v0.1.0-beta'}, {'tag_name': '../anything'}, {'tag_name': 'v01.0.0'}]:
            with self.subTest(release=release), self.assertRaises(ValueError):
                updater.compare_release('0.1.0', release)

    def test_update_check_only_requests_public_metadata_and_changes_no_files(self):
        requests = []

        def opener(request, timeout):
            requests.append((request.full_url, request.data, timeout))
            return io.BytesIO(json.dumps({'tag_name': 'v0.2.0'}).encode())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'VERSION').write_text('0.1.0\n')
            result = updater.check_update(root, opener)
            self.assertEqual(result['status'], 'update_available')
            self.assertEqual(requests, [(updater.API_URL, None, 10)])
            self.assertEqual(list(root.iterdir()), [root / 'VERSION'])
            self.assertEqual((root / 'VERSION').read_text(), '0.1.0\n')

    def test_network_failures_do_not_claim_latest(self):
        for error, expected in [(URLError('offline'), 'unavailable'),
                                (HTTPError(updater.API_URL, 403, 'Rate limited', {}, None), 'unavailable'),
                                (HTTPError(updater.API_URL, 404, 'No release', {}, None), 'no_published_release')]:
            def opener(request, timeout):
                raise error
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                result = updater.check_update(Path(directory), opener)
                self.assertEqual(result['status'], expected)
                self.assertFalse(result['updated_files'])

    def test_invalid_response_is_reported_unavailable(self):
        for payload in [b'not-json', b'[]', b'x' * 1_048_577]:
            def opener(request, timeout):
                return io.BytesIO(payload)
            with self.subTest(length=len(payload)), tempfile.TemporaryDirectory() as directory:
                self.assertEqual(updater.check_update(Path(directory), opener)['status'], 'unavailable')


class ReleaseTests(unittest.TestCase):
    def test_package_is_minimal_reproducible_and_runs_in_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            one = builder.build(ROOT, target / 'one')
            two = builder.build(ROOT, target / 'two')
            self.assertEqual(one['sha256'], two['sha256'])
            archive = Path(one['archive'])
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), one['sha256'])
            self.assertEqual((target / 'one/SHA256SUMS').read_text(), one['sha256'] + '  clear-output.zip\n')
            with zipfile.ZipFile(archive) as package:
                paths = set(package.namelist())
                for name in ['SKILL.md', 'VERSION', 'LICENSE', 'CHANGELOG.md', 'scripts/clear_output.py',
                             'scripts/check_update.py', 'references/checks.md', 'references/updates.md',
                             'references/glossary.example.json', 'agents/openai.yaml']:
                    self.assertIn('clear-output/' + name, paths)
                self.assertFalse(any('/tests/' in p or '/evals/' in p or '/assets/' in p or '/__pycache__/' in p for p in paths))
                package.extractall(target / 'install')
            installed = target / 'install/clear-output'
            answer = target / '中文.txt'
            answer.write_text('构建完成。开始测试。通过后部署。', encoding='utf-8')
            run = subprocess.run([sys.executable, str(installed / 'scripts/clear_output.py'), str(answer), '--lang', 'zh'],
                                 capture_output=True, encoding='utf-8')
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['metrics']['sentences_or_lines'], 3)

    def test_tag_version_must_match(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            builder.build(ROOT, Path(directory), tag='v999.0.0')


if __name__ == '__main__':
    unittest.main()
