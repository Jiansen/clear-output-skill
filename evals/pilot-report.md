# Development pilot — 2026-11-08

**The skill handled a Chinese-to-English debugging switch that both comparison conditions missed. It did not improve the overall initial pass count.** It also missed an operational clarification in one case; a narrow revision addressed that omission in a follow-up test.

中文结论：这次实测支持“一个技能兼容中英任务”的设计，但不能证明完整技能普遍优于简短提示。首轮发现的遗漏已保留，并完成了修订复测。

## What ran

- 24 synthetic conversations × 3 conditions = 72 initial responses.
- One independent subject agent per condition, with no inherited parent conversation. Each received the same case inputs and its assigned guidance, without the rubric.
- One separate reviewer saw shuffled responses without condition labels, alongside the source conversations and frozen invariants.
- After one skill revision, a fresh subject answered two regression cases and eight new transfer cases. Another reviewer evaluated these 10 responses.
- Total: **82 generated responses**. Both independent reviews and developer adjudication were performed by AI agents, not human participants.

The exact model revision and sampling parameters were not exposed by the host. Each condition was a single batch, not 24 isolated contexts. See [the environment manifest](results/environment.json) and [protocol](README.md).

## Initial results

| Condition | Independent review | After documented adjudication | Mean clarity score (1–5) |
| --- | --- | --- | --- |
| Normal behavior | 23 pass, 1 fail | 23/24 pass | 5.000 |
| Short clarity prompt | 23 pass, 1 fail | 23/24 pass | 5.000 |
| Initial full skill | 23 pass, 1 needs review | 23/24 pass | 4.958 |

The near-ceiling clarity scores are subjective model judgments. They do not demonstrate better human comprehension or a meaningful difference between conditions.

All three response bundles passed the limited deterministic checks for coverage, selected literals, and format. That result did **not** detect the semantic/language findings below.

### c03: English debugging after Chinese context

The earlier exchange was Chinese, but the current user request was English:

> The failing test says `expected 2 calls, received 3`. Explain what this establishes and give one next debugging step. We have not inspected the call sites yet.

Both normal behavior and the short prompt answered in Chinese. The skill answered in English and kept the distinction between the observed call-count mismatch and an unknown cause. This is one observed language-routing improvement, not a measured general success rate.

### c12: Missing valve identity

Source instruction:

> 打开阀门，直到压力低于 5。

The initial skill response asked about the pressure unit, measurement point/reference, and operation at the stopping condition, but did not ask which valve. The independent reviewer marked this `needs_review`: the rubric phrase “valve/pressure measurement” did not clearly say whether both were mandatory.

The development agent conservatively counted it as a failure under the intended requirement to identify both the valve and the measurement. The original rubric and review remain unchanged; [adjudications.json](results/adjudications.json) records this decision. The re-test reviewer received that explicit interpretation.

## Revision and re-test

One sentence pair was added to the procedure guidance: when identifying missing operational information, check the object/actor as well as quantities, units, measurement references, and start/stop conditions; ask for necessary facts without inventing them. The original version is preserved in [snapshots/initial-skill.txt](snapshots/initial-skill.txt).

The revised skill passed **10/10 cases and 30/30 listed invariants** in a new subject/reviewer pass:

- Regression: c03 stayed English; c12 asked for the valve, pressure measurement, and unit.
- Eight new transfer cases: missing object and measurement details; language switching; English release notes with Chinese commentary; Chinese JSON; permissions, limits, and approximation; simultaneous actions; exact command and mixed-language log preservation.

The new cases and criteria were fixed before the re-test responses were generated, but were authored by the same developer after seeing the initial failure. Only the skill condition was re-tested. These results cannot be compared as a new 32-case win rate against the two baseline conditions.

The official skill-package validator passed. The 11 evaluation-helper tests passed locally; the GitHub workflow runs those tests and checks the published response contracts. These are tooling checks, not additional model-behavior cases.

## Evidence

| Artifact | Contents |
| --- | --- |
| [baseline.json](results/baseline.json) | 24 normal responses |
| [short-prompt.json](results/short-prompt.json) | 24 short-prompt responses |
| [full-skill.json](results/full-skill.json) | 24 initial skill responses, including the omission |
| [blind-review.json](results/blind-review.json) | All initial invariant judgments and clarity notes |
| [blind-map.json](results/blind-map.json) | Published mapping from anonymous sample IDs to conditions |
| [adjudications.json](results/adjudications.json) | One explicit adjudication; original review preserved |
| [revised-skill.json](results/revised-skill.json) | 10 revised-skill responses |
| [retest-review.json](results/retest-review.json) | Re-test invariant judgments |
| [environment.json](results/environment.json) | Method and skill/fixture hashes |

Recompute counts with:

```bash
python3 tools/summarize_pilot.py
```

## What remains untested

Automatic skill selection by a host, interaction with other simultaneously active skills, long conversations, different model families, repeated samples, and human time-to-understanding were not evaluated. Explicitly loading the skill tests its instructions; it does not establish automatic activation reliability.

The next useful evaluation is a fresh set of authentic but publishable tasks, multiple samples in isolated contexts, and human review of accuracy and reading effort. Keep failures and compare against the short prompt again.
