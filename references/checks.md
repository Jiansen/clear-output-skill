# Optional checks

Use `scripts/clear_output.py` when a substantial rewrite, output contract, or project glossary warrants repeatable checks. The skill still works without Python. The checker needs Python 3.10+ and its standard library; it makes no network or model calls and never edits input files.

Run from the skill directory, or use the script's absolute path. Input paths refer to the caller's current directory:

```bash
python3 scripts/clear_output.py answer.md --lang en
python3 scripts/clear_output.py answer.md --lang zh --source original.md --contract contract.json
python3 scripts/clear_output.py answer.md --lang mixed --glossary glossary.json
```

Choose `--lang` from the user's requested artifact language. An English debug explanation containing a quoted Chinese error stays `en`. A Chinese explanation with English identifiers can use `zh`; use `mixed` when both languages are deliberately used in prose. Do not use the checker's coarse script counts to override an explicit language request.

## What is checked

| Check | Scope | Finding |
| --- | --- | --- |
| Required literals | Exact strings explicitly listed in the contract, anywhere in the output | `error` if missing |
| JSON | Raw JSON syntax, duplicate keys, optional exact top-level key set | `error` |
| Language | Obvious mismatch between selected profile and prose script counts | `review`; not language certification |
| Quantities in a rewrite | Arabic numerals, selected units, occurrence counts; exact time-unit normalization | `review` |
| Meaning markers in a rewrite | Changes in counts of markers for possibility, advice, obligation, permission/capability, approximation, negation, conditions, bounds, or concurrency | `review` |
| Project terms | Configured alternatives outside protected spans, with phrase exceptions | `style` |
| Length | English word or Chinese Han-character counts against thresholds you explicitly supply | `style` |

Findings contain rule IDs, evidence, and one-based line/column locations when available. A missing item may have no output location; meaning findings can include the source location. `error` means an explicit mechanical contract failed. `review` requires context. `style` is optional advice. There is no quality or compliance score.

Only `error` findings produce exit code 1 by default. Use `--fail-on review` to also fail on review findings, or `--fail-on style` to include all findings. Exit code 2 means invalid input/configuration. An exit code of 0 does not mean no review is needed: inspect `status`, `diagnostics`, and `coverage`.

## Contracts and authorized changes

Example `contract.json`:

```json
{
  "format": "json",
  "json_keys": ["observation", "next_step"],
  "required_literals": ["ECONNRESET"]
}
```

For prose, use `"format": "text"` and omit `json_keys`. `required_literals` is optional. Preserve only strings the task actually requires; do not lock all source text by default. When a task authorizes changing a command, path, value, or unit, reflect that scope in the contract rather than reverting the authorized edit to satisfy a check. Unknown configuration keys and duplicate JSON keys are rejected.

The JSON check does not validate value types or a full JSON Schema. Required literals are presence checks, not assertions about where a string appears or whether it is used correctly. For structured data, use the task's actual schema validator as well. JSON documents skip prose/source-comparison heuristics and report that skipped scope.

## Separate English and Chinese rules

The scanner recognizes `。！？` and English sentence punctuation, keeps decimals and common English abbreviations together, and treats display newlines as additional boundaries. `sentences_or_lines` describes that convention; it is not a linguistic sentence count for arbitrarily wrapped prose.

English words and Chinese Han characters are counted separately, including in mixed text. Pure Chinese never receives an invented English word count or a perfect score. Length advice is opt-in because this project has not calibrated a universal readability threshold:

```bash
python3 scripts/clear_output.py answer.md --lang mixed --max-en-words 30 --max-zh-chars 60
```

Those example limits are a local editing preference, not an ASD requirement or proven readability boundary. There are no universal bans on passive voice, perfect tenses, Chinese omitted subjects, or words such as `may`, `should`, `约`, and `建议`.

Use [glossary.example.json](glossary.example.json) as a project glossary format. Each entry can define `en`, `zh`, or both, with `preferred`, `avoid`, and optional `except` phrases. Only the selected language profile is used; `mixed` uses both. The example is not an automatically loaded dictionary. Keep technical meanings distinct. Chinese matching uses configured phrases, not a general Chinese word segmenter; use exception phrases when an alternative can occur inside a legitimate term.

## Protected content and limits

The conservative Markdown scanner masks backtick and tilde code fences (including an unclosed fence through EOF), inline code, indented lines, blockquotes, common double/Chinese quotes, link destinations, URLs, and HTML tags. It removes common list/emphasis markers, so numbering steps or bolding a quantity does not introduce factual numbers. It preserves offsets for findings. Tables participate in quantity comparison but are excluded from sentence-length checks. These exclusions also apply to meaning-marker comparison; a quote is protected content, not automatically analyzed prose. Exact contract checks still inspect the full output.

This is not a complete CommonMark, HTML, programming-language, or log parser. For unusual nesting, raw logs, or exact quotations, delimit them explicitly or declare the required literals. Code-only input reports prose as `not_checked` rather than implying it passed a writing assessment.

Source comparison is deliberately limited. It compares quantity multisets, so it cannot catch the same numbers assigned to different actors, reordered bounds, or swapped units attached to different items. It normalizes exact second/millisecond/minute/hour conversions and comma thousands separators, but does not interpret scientific notation, Chinese numeral words, every unit, dates, or rounding. Marker counts can miss a changed condition with the same words, and can flag a harmless paraphrase. `May` can be a month; `can` can indicate permission or ability. Review these findings; do not auto-fix them.

Check facts, actors, objects, scope, order, uncertainty, and causal relationships against the source even when no findings remain. For diagrams/HTML, follow [output-forms.md](output-forms.md): syntax/rendering and meaningful interaction require the appropriate host tools. This text checker does not validate diagram topology or browser behavior.
