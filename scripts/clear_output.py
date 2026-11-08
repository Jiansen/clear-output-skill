#!/usr/bin/env python3
"""Optional local checks for English, Chinese, and mixed technical writing.

No model calls, automatic edits, network access, or compliance score.
Python 3.10+, standard library only. See references/checks.md for scope.
"""

import argparse
from collections import Counter
from decimal import Decimal, localcontext
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EN_WORD = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002ebef]")
ABBREVIATIONS = {'mr', 'mrs', 'ms', 'dr', 'prof', 'e.g', 'i.e', 'fig', 'approx', 'vs'}
MARKERS = {
    'possibility': r'\b(?:may|might|could|possibly|perhaps)\b|可能|也许|或许',
    'recommendation': r'\b(?:should|recommend|recommended)\b|建议',
    'obligation': r'\b(?:must|required)\b|必须|务必',
    'permission_or_capability': r'\bcan\b|可以|能够',
    'approximation': r'\b(?:about|approximately|roughly)\b|大约|约(?=[\s\d零一二三四五六七八九十两])',
    'negation': r"\b(?:not|never|cannot|no)\b|\b\w+n['’]t\b|不要|不得|不能|不会|不应|没有",
    'condition': r'\b(?:if|unless)\b|如果|除非|仅当|只有',
    'lower_bound': r'\bat least\b|至少|不低于',
    'upper_bound': r'\bat most\b|至多|不高于',
    'concurrency': r'\b(?:parallel|concurrently|simultaneously)\b|并行|同时',
}
TIME_UNITS = {
    'ms': Decimal('.001'), 'millisecond': Decimal('.001'), 'milliseconds': Decimal('.001'), '毫秒': Decimal('.001'),
    's': Decimal(1), 'sec': Decimal(1), 'second': Decimal(1), 'seconds': Decimal(1), '秒': Decimal(1),
    'min': Decimal(60), 'minute': Decimal(60), 'minutes': Decimal(60), '分钟': Decimal(60),
    'h': Decimal(3600), 'hour': Decimal(3600), 'hours': Decimal(3600), '小时': Decimal(3600),
}
UNIT_PATTERN = '|'.join(re.escape(x) for x in sorted(
    list(TIME_UNITS) + ['KiB', 'MiB', 'GiB', 'KB', 'MB', 'GB', 'bytes', 'byte', '%', '°C', '°F'], key=len, reverse=True))
QUANTITY = re.compile(r'(?<![A-Za-z0-9_.])(?P<number>[+-]?(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+))'
                      r'(?:\s*(?P<unit>' + UNIT_PATTERN + r')(?![A-Za-z]))?')


def version():
    path = ROOT / 'VERSION'
    return path.read_text(encoding='utf-8').strip() if path.exists() else 'unversioned'


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result

    def reject(value):
        raise ValueError('Non-JSON constant: ' + value)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=reject)


def prose_view(text):
    """Mask common Markdown protected spans, preserving original offsets.

    A conservative scanner, not a full Markdown/HTML parser. Tables stay visible
    for quantity comparison; style checks skip table rows. Unterminated fences
    are protected through EOF. Quoted examples are deliberately not style-edited.
    """
    chars = list(text)
    excluded = Counter()

    def mask(start, end, kind):
        excluded[kind] += 1
        for index in range(start, end):
            if chars[index] not in '\r\n':
                chars[index] = ' '

    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        if fence:
            mask(offset, offset + len(line), 'fenced_code_lines')
            if re.fullmatch(r' {0,3}' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}[ \t]*\r?\n?', line):
                fence = None
        else:
            opening = re.match(r' {0,3}(`{3,}|~{3,})', line)
            if opening:
                fence = (opening[1][0], len(opening[1]))
                mask(offset, offset + len(line), 'fenced_code_lines')
            elif re.match(r' {0,3}>', line):
                mask(offset, offset + len(line), 'block_quote_lines')
            elif line.startswith(('    ', '\t')):
                mask(offset, offset + len(line), 'indented_lines')
            else:
                marker = re.match(r' {0,3}(?:\d{1,9}[.)]|[-*+])[ \t]+', line)
                if marker:
                    mask(offset, offset + marker.end(), 'list_markers')
        offset += len(line)

    view = ''.join(chars)
    cursor = 0
    while cursor < len(view):
        opening = re.search(r'`+', view[cursor:])
        if not opening:
            break
        start = cursor + opening.start()
        end = cursor + opening.end()
        closing = re.search(r'(?<!`)' + re.escape(opening[0]) + r'(?!`)', view[end:])
        if closing:
            close_end = end + closing.end()
            mask(start, close_end, 'inline_code')
            cursor = close_end
        else:
            cursor = end

    patterns = [
        ('quoted_text', r'“[^”]*”|「[^」]*」|『[^』]*』|"[^"\n]*"'),
        ('link_destination', r'\]\((?:\\.|[^()\\]|\([^()]*\))*\)'),
        ('url', r'https?://[^\s<>"`，。！？；、）]+'),
        ('html_tag', r'<[^>\n]+>'),
    ]
    for kind, pattern in patterns:
        for match in re.finditer(pattern, ''.join(chars)):
            # Keep the closing bracket of the visible link label.
            mask(match.start() + (1 if kind == 'link_destination' else 0), match.end(), kind)
    for match in re.finditer(r'(?<!\w)(\*\*|__|\*|_)(?=\S)([^\n]+?)(?<=\S)\1(?!\w)', ''.join(chars)):
        mask(match.start(), match.start(2), 'emphasis_markers')
        mask(match.end(2), match.end(), 'emphasis_markers')
    return ''.join(chars), dict(excluded)


def sentences(view):
    """Yield (offset, text) for prose; count both CJK and Latin boundaries."""
    # Mask headings/list prefixes, and skip table rows for sentence style only.
    chars = list(view)
    offset = 0
    for line in view.splitlines(keepends=True):
        prefix = re.match(r'\s*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)', line)
        if line.lstrip().startswith('|'):
            chars[offset:offset + len(line)] = ['\n' if c == '\n' else ' ' for c in line]
        elif prefix:
            chars[offset:offset + prefix.end()] = [' '] * prefix.end()
        offset += len(line)
    value = ''.join(chars)
    start = 0
    for index, char in enumerate(value):
        end = char in '。！？!?'
        if char == '.' and (index + 1 == len(value) or value[index + 1].isspace()):
            before = value[start:index]
            last = re.search(r'([A-Za-z.]+)$', before)
            end = not (last and last[1].lower() in ABBREVIATIONS)
        if char == '\n':
            # Display lines are boundaries; report this convention in the docs.
            end = True
        if end:
            part = value[start:index + 1]
            if part.strip():
                leading = len(part) - len(part.lstrip())
                yield start + leading, part.strip()
            start = index + 1
    if value[start:].strip():
        part = value[start:]
        yield start + len(part) - len(part.lstrip()), part.strip()


def location(text, index):
    if index is None:
        return None
    return {'line': text.count('\n', 0, index) + 1,
            'column': index - text.rfind('\n', 0, index)}


def term_matches(text, term):
    # Latin terms use identifier boundaries; Chinese terms match complete
    # configured strings, with optional project-specific exception phrases.
    left = r'(?<![A-Za-z0-9_])' if term[0].isascii() and term[0].isalnum() else ''
    right = r'(?![A-Za-z0-9_])' if term[-1].isascii() and term[-1].isalnum() else ''
    return re.finditer(left + re.escape(term) + right, text, re.IGNORECASE)


def validate_settings(contract, glossary):
    if not isinstance(contract, dict) or set(contract) - {'format', 'required_literals', 'json_keys'}:
        raise ValueError('Contract supports only format, required_literals, and json_keys.')
    if contract.get('format', 'text') not in ('text', 'json'):
        raise ValueError('format must be text or json.')
    for key in ('required_literals', 'json_keys'):
        if key in contract and (not isinstance(contract[key], list) or
                                any(not isinstance(x, str) or not x for x in contract[key])):
            raise ValueError(key + ' must be a list of nonempty strings.')
        if key in contract and len(set(contract[key])) != len(contract[key]):
            raise ValueError(key + ' must not contain duplicates.')
    if 'json_keys' in contract and contract.get('format') != 'json':
        raise ValueError('json_keys requires format=json.')
    if not isinstance(glossary, dict) or set(glossary) != {'terms'} or not isinstance(glossary['terms'], list):
        raise ValueError('Glossary must contain a terms list.')
    for term in glossary['terms']:
        if not isinstance(term, dict) or set(term) - {'id', 'en', 'zh'} or not isinstance(term.get('id'), str):
            raise ValueError('Each glossary entry requires id and en and/or zh.')
        if not ({'en', 'zh'} & set(term)):
            raise ValueError('A glossary entry needs at least one language.')
        for lang in ('en', 'zh'):
            if lang not in term:
                continue
            rule = term[lang]
            if not isinstance(rule, dict) or set(rule) - {'preferred', 'avoid', 'except'}:
                raise ValueError('A language entry supports preferred, avoid, and except.')
            if not isinstance(rule.get('preferred'), str) or not rule['preferred']:
                raise ValueError('A glossary preferred term must be a nonempty string.')
            for key in ('avoid', 'except'):
                values = rule.get(key, [])
                if not isinstance(values, list) or any(not isinstance(x, str) or not x for x in values):
                    raise ValueError('Glossary ' + key + ' must be a list of nonempty strings.')


def quantities(view):
    values = Counter()
    for match in QUANTITY.finditer(view):
        value = Decimal(match['number'].replace(',', ''))
        unit = match['unit'] or ''
        with localcontext() as context:
            context.prec = max(28, len(value.as_tuple().digits) + 8)
            if unit in TIME_UNITS:
                value *= TIME_UNITS[unit]
                unit = 'seconds'
            values[(str(value.normalize()), unit)] += 1
    return values


def check(text, lang, source=None, contract=None, glossary=None, max_en_words=None, max_zh_chars=None):
    if lang not in ('en', 'zh', 'mixed'):
        raise ValueError('Choose en, zh, or mixed from the task; do not infer it from quoted text.')
    contract = {} if contract is None else contract
    glossary = {'terms': []} if glossary is None else glossary
    validate_settings(contract, glossary)
    for limit in (max_en_words, max_zh_chars):
        if limit is not None and (type(limit) is not int or limit < 1):
            raise ValueError('Length thresholds must be positive integers.')
    diagnostics = []

    def add(rule, severity, message, index=None, **evidence):
        diagnostics.append({'rule': rule, 'severity': severity, 'message': message,
                            'location': location(text, index), **evidence})

    if not text.strip():
        add('format.empty', 'error', 'The output is empty.')
    for literal in contract.get('required_literals', []):
        if literal not in text:
            add('literal.missing', 'error', 'A required exact literal is missing.', expected=literal)

    is_json = contract.get('format') == 'json'
    if is_json:
        try:
            parsed = strict_json(text)
        except ValueError as error:
            add('format.json', 'error', str(error))
        else:
            if 'json_keys' in contract and (not isinstance(parsed, dict) or set(parsed) != set(contract['json_keys'])):
                add('format.json_keys', 'error', 'Expected exactly the configured top-level JSON keys.', expected=contract['json_keys'])

    view, excluded = prose_view(text) if not is_json else ('', {'json_document': 1})
    chunks = list(sentences(view))
    en_count, zh_count = len(EN_WORD.findall(view)), len(HAN.findall(view))
    has_prose = bool(en_count or zh_count)
    if not is_json:
        if lang == 'en' and zh_count >= 6 and zh_count > en_count * 4:
            add('language.review', 'review', 'Substantial Chinese prose conflicts with the requested English profile.')
        if lang == 'zh' and zh_count == 0 and en_count >= 8:
            add('language.review', 'review', 'English-only prose may conflict with the requested Chinese profile.')
        for start, sentence in chunks:
            words, han = len(EN_WORD.findall(sentence)), len(HAN.findall(sentence))
            if lang in ('en', 'mixed') and max_en_words is not None and words > max_en_words:
                add('style.en_length', 'style', 'Consider splitting this long English sentence or display line.', start,
                    actual=words, threshold=max_en_words)
            if lang in ('zh', 'mixed') and max_zh_chars is not None and han > max_zh_chars:
                add('style.zh_length', 'style', 'Consider splitting this long Chinese sentence or display line.', start,
                    actual=han, threshold=max_zh_chars)
        for entry in glossary['terms']:
            for profile in ('en', 'zh') if lang == 'mixed' else (lang,):
                if profile not in entry:
                    continue
                rule = entry[profile]
                exceptions = [m.span() for term in rule.get('except', []) + [rule['preferred']] for m in term_matches(view, term)]
                for alternative in rule.get('avoid', []):
                    for match in term_matches(view, alternative):
                        if any(start <= match.start() and match.end() <= end for start, end in exceptions):
                            continue
                        add('term.preference', 'style', 'Consider the project term if the meaning is the same.', match.start(),
                            term_id=entry['id'], found=match[0], preferred=rule['preferred'], language=profile)

    comparison = 'not_requested'
    if source is not None and not is_json:
        source_view, _ = prose_view(source)
        comparison = 'heuristics_only'
        before, after = quantities(source_view), quantities(view)
        if before != after:
            def describe(counter):
                return [{'value': key[0], 'unit': key[1], 'count': count} for key, count in sorted(counter.items())]
            add('meaning.quantities', 'review', 'Numeric quantities changed; check values, units, and scope. This may be an authorized edit.',
                removed=describe(before - after), added=describe(after - before))
        for category, pattern in MARKERS.items():
            before_matches = list(re.finditer(pattern, source_view, re.IGNORECASE))
            after_matches = list(re.finditer(pattern, view, re.IGNORECASE))
            if len(before_matches) != len(after_matches):
                add('meaning.' + category, 'review', 'Meaning-bearing markers changed; compare the source and output in context.',
                    after_matches[0].start() if after_matches else None,
                    source_count=len(before_matches), output_count=len(after_matches),
                    source_location=location(source, before_matches[0].start() if before_matches else None))
    elif source is not None:
        comparison = 'skipped_json'

    counts = {level: sum(d['severity'] == level for d in diagnostics) for level in ('error', 'review', 'style')}
    status = ('errors' if counts['error'] else 'review' if counts['review'] else 'suggestions' if counts['style']
              else 'no_findings' if has_prose or is_json or contract.get('required_literals') else 'not_checked')
    return {
        'version': version(), 'status': status, 'language_profile': lang,
        'summary': counts, 'diagnostics': diagnostics,
        'metrics': {'sentences_or_lines': len(chunks), 'english_words': en_count, 'han_characters': zh_count},
        'coverage': {'format': contract.get('format', 'text'), 'required_literals': len(contract.get('required_literals', [])),
                     'prose': 'checked_heuristically' if has_prose else 'not_checked', 'excluded_spans': excluded,
                     'source_comparison': comparison, 'semantic_equivalence': 'not_verified',
                     'length_thresholds': {'en_words': max_en_words, 'zh_characters': max_zh_chars},
                     'glossary_entries': len(glossary['terms'])},
    }


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='UTF-8 output text or Markdown file')
    parser.add_argument('--lang', required=True, choices=['en', 'zh', 'mixed'])
    parser.add_argument('--source', type=Path, help='Original text for a faithful rewrite; omit for a new explanation')
    parser.add_argument('--contract', type=Path, help='JSON with required_literals, format, and optional json_keys')
    parser.add_argument('--glossary', type=Path, help='Optional project glossary JSON')
    parser.add_argument('--max-en-words', type=int)
    parser.add_argument('--max-zh-chars', type=int)
    parser.add_argument('--fail-on', choices=['error', 'review', 'style'], default='error')
    parser.add_argument('--version', action='version', version=version())
    args = parser.parse_args()
    try:
        report = check(args.input.read_text(encoding='utf-8'), args.lang,
                       source=args.source.read_text(encoding='utf-8') if args.source else None,
                       contract=strict_json(args.contract.read_text(encoding='utf-8')) if args.contract else None,
                       glossary=strict_json(args.glossary.read_text(encoding='utf-8')) if args.glossary else None,
                       max_en_words=args.max_en_words, max_zh_chars=args.max_zh_chars)
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({'status': 'invalid_input', 'error': str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    levels = ['error', 'review', 'style']
    return int(any(report['summary'][level] for level in levels[:levels.index(args.fail_on) + 1]))


if __name__ == '__main__':
    sys.exit(main())
