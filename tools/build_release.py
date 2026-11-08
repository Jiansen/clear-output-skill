#!/usr/bin/env python3
"""Build a deterministic, minimal skill ZIP and checksum; never publish it."""

import argparse
import hashlib
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build(root, output, tag=None):
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)', version):
        raise ValueError('VERSION must contain a stable major.minor.patch version.')
    if tag is not None and tag != 'v' + version:
        raise ValueError('Release tag does not match VERSION.')
    skill = (root / 'SKILL.md').read_text(encoding='utf-8')
    if not re.search(r'^  version: "' + re.escape(version) + r'"$', skill, re.MULTILINE):
        raise ValueError('SKILL.md metadata.version does not match VERSION.')
    changelog = (root / 'CHANGELOG.md').read_text(encoding='utf-8')
    match = re.search(r'^## \[' + re.escape(version) + r'\][^\n]*\n([\s\S]*?)(?=^## |\Z)', changelog, re.MULTILINE)
    if not match:
        raise ValueError('The release needs a CHANGELOG.md entry.')
    files = [root / name for name in ['SKILL.md', 'VERSION', 'LICENSE', 'CHANGELOG.md']]
    for directory, extensions in [('references', {'.md', '.json'}), ('scripts', {'.py'}), ('agents', {'.yaml'})]:
        files.extend(p for p in (root / directory).rglob('*') if p.suffix in extensions and '__pycache__' not in p.parts)
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError('Release inputs must be regular files: ' + str(path))
    output.mkdir(parents=True, exist_ok=True)
    archive = output / 'clear-output.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for path in sorted(files):
            info = zipfile.ZipInfo('clear-output/' + path.relative_to(root).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, path.read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / 'SHA256SUMS').write_text(digest + '  clear-output.zip\n', encoding='utf-8')
    (output / 'release-notes.md').write_text(match[1].strip() + '\n', encoding='utf-8')
    return {'version': version, 'archive': str(archive), 'sha256': digest, 'files': len(files)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--tag')
    args = parser.parse_args()
    print(build(ROOT, args.output_dir, args.tag))
