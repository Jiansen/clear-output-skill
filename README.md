# Clear Output

[简体中文](README.zh-CN.md)

One skill for clearer Chinese, English, and mixed-language technical communication through words, diagrams, and interaction. It helps the reader understand and verify the result while preserving language, factual meaning, uncertainty, and technical literals.

Use it for debugging explanations, mechanisms, comparisons, status updates, instructions, and faithful rewrites. It is an instruction-only skill with no required runtime or background service. Producing visual artifacts uses whatever rendering tools the host provides; the skill does not depend on a specific plugin. The core evaluation helpers use Python's standard library; optional rendered-artifact checks use Node.js browser tooling.

## What it does

- Chooses language from the user's request and the artifact being edited. An English debugging conversation stays English. A Chinese question about an English log gets a Chinese explanation with the log intact.
- Preserves facts, conditions, exceptions, approximate values, permissions, and recommendations. `May` does not become `will`; `约 5 秒` does not become an exact delay.
- Separates observed behavior from hypotheses and verified outcomes.
- Chooses the representation before polishing the wording: a table for shared criteria, a diagram for branches and dependencies, a chart for measured patterns, interaction for exploring variables, or animation/video for a mechanism that develops over time.
- Proactively creates a useful visual within the task's scope, checks the rendered result when possible, and distinguishes source/storyboards from working artifacts. A short factual answer can stay one sentence.

The skill applies to the current task. It does not turn the whole conversation into a permanent language or style mode. It does not check whether source facts are true, and it does not certify ASD-STE100 compliance.

## Install and use

In Codex, ask the built-in installer:

```text
$skill-installer install https://github.com/Jiansen/clear-output-skill
```

The skill is at the repository root; its name is `clear-output`. To install manually in the current documented Codex user location:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Jiansen/clear-output-skill.git ~/.agents/skills/clear-output
```

Use one installation method to avoid duplicate entries. Host versions can use different skill directories; the built-in installer follows its host's configuration. See [Codex skill documentation](https://developers.openai.com/codex/skills).

Examples:

```text
$clear-output Explain this failing test in English. Keep the error text unchanged.
```

```text
$clear-output 帮我改清楚这段说明，保留原意、数值和不确定性。
```

```text
$clear-output 润色下面的英文 README，正文保持英文，用中文解释修改。
```

The description also permits the host to select the skill for matching tasks. Explicit invocation is useful when testing; automatic selection is host-dependent.

## A small example

Source:

> 建议先备份配置。等待约 5 秒后，可以重试；如果任务已取消，则不要重试。

A faithful revision:

> 建议先备份配置。如果任务已取消，不要重试。否则，等待约 5 秒后，可以重试。

The backup remains a recommendation, the delay remains approximate, and retry remains optional. Inventing a deadline or turning each sentence into an order would change the meaning.

## Test it

The first pilot contains 24 synthetic cases, a frozen semantic rubric, and three conditions: normal behavior, a short clarity prompt, and the full skill. See [the evaluation protocol](evals/README.md) and [the pilot report](evals/pilot-report.md) for actual outputs and limitations. A [follow-up evaluation](evals/form-report.md) compares the previous and expanded representation guidance and tests a real interactive artifact.

Try the self-contained [exponential-backoff explorer](examples/retry-backoff.html): change the delay and retry count to see individual waits and their total. Download/open the HTML locally; GitHub's source view does not run it.

```bash
python3 -m unittest discover -s tests -v
python3 tools/make_prompt.py full-skill > /tmp/clear-output-prompt.txt
python3 tools/check_responses.py evals/results/full-skill.json
```

The checker validates response coverage, selected literal preservation, and output contracts. **It cannot establish semantic equivalence or writing quality.** Semantic review is reported separately. The published pilot is a small development test, not evidence that a longer prompt generally improves a model.

## Project structure

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Runtime instructions and activation description |
| [references/edge-cases.md](references/edge-cases.md) | Examples for difficult rewrites |
| [references/output-forms.md](references/output-forms.md) | Choosing and checking diagrams, charts, interaction, and media |
| [agents/openai.yaml](agents/openai.yaml) | Codex display metadata |
| [evals/](evals/) | Test inputs, criteria, raw responses, and review |
| [tools/](tools/) | Local evaluation helpers; not needed to use the skill |
| [examples/](examples/) | An actual generated and browser-tested explanation |

## Origins and contributions

The project takes inspiration from [Andrej Karpathy's discussion of clearer AI output](https://x.com/karpathy/status/2105819303471976479), [ASD-STE100](https://www.asd-ste100.org/), and the open-source projects listed in [ATTRIBUTION.md](ATTRIBUTION.md). These are original bilingual instructions, not an official Chinese edition or a reproduction of the ASD dictionary.

Contributions should include a realistic failure case, the intended semantic invariants, and before/after responses. Prefer a narrow, demonstrated correction over adding universal rules. Keep evaluation inputs synthetic or explicitly licensed for publication.

MIT licensed. See [LICENSE](LICENSE).
