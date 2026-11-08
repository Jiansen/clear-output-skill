#!/usr/bin/env python3
"""Explicit, read-only update check. Requests public GitHub release metadata only."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'Jiansen/clear-output-skill'
API_URL = 'https://api.github.com/repos/' + REPOSITORY + '/releases/latest'
RELEASES_URL = 'https://github.com/' + REPOSITORY + '/releases'


def parse_version(value):
    if not isinstance(value, str) or not re.fullmatch(r'(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)', value):
        raise ValueError('Expected a stable major.minor.patch version.')
    return tuple(int(part) for part in value.split('.'))


def compare_release(installed, release):
    if not isinstance(release, dict) or release.get('draft') or release.get('prerelease'):
        raise ValueError('The response is not a published stable release.')
    tag = release.get('tag_name', '')
    if not isinstance(tag, str) or not tag.startswith('v'):
        raise ValueError('The latest release has an unsupported tag.')
    latest = tag[1:]
    remote = parse_version(latest)
    if installed is None:
        status = 'installed_version_unknown'
    else:
        local = parse_version(installed)
        status = 'update_available' if local < remote else 'same_version' if local == remote else 'local_ahead'
    return {'status': status, 'installed': installed, 'latest': latest,
            'release_url': RELEASES_URL + '/tag/' + tag,
            'download_url': RELEASES_URL + '/download/' + tag + '/clear-output.zip',
            'updated_files': False}


def check_update(root=ROOT, opener=urlopen):
    version_file = root / 'VERSION'
    installed = version_file.read_text(encoding='utf-8').strip() if version_file.is_file() else None
    if installed is not None:
        parse_version(installed)
    request = Request(API_URL, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'clear-output-update-check'})
    try:
        with opener(request, timeout=10) as response:
            # Release notes are not executed or injected into model instructions.
            payload = response.read(1_048_577)
            if len(payload) > 1_048_576:
                raise ValueError('Unexpectedly large release metadata.')
            release = json.loads(payload)
        return compare_release(installed, release)
    except HTTPError as error:
        error.close()
        return {'status': 'no_published_release' if error.code == 404 else 'unavailable',
                'installed': installed, 'http_status': error.code, 'release_url': RELEASES_URL, 'updated_files': False}
    except (URLError, OSError, ValueError) as error:
        return {'status': 'unavailable', 'installed': installed, 'error': str(error),
                'release_url': RELEASES_URL, 'updated_files': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        result = check_update()
    except (OSError, UnicodeError, ValueError) as error:
        result = {'status': 'invalid_local_version', 'error': str(error), 'updated_files': False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result['status'] in ('unavailable', 'invalid_local_version') else 0


if __name__ == '__main__':
    sys.exit(main())
