# Evaluation protocol

This is a development evaluation of a writing skill, not an ASD compliance test or a human-comprehension study. All task content is synthetic. It contains no production data, credentials, or private user messages.

The later [representation and artifact evaluation](form-report.md) tests diagrams, output-format boundaries, and an actual interactive explanation. It keeps source-level judgments separate from rendered-artifact checks.

## Conditions

| Condition | Additional guidance |
| --- | --- |
| `baseline` | Normal writing behavior |
| `short-prompt` | "Write clearly and concisely. Preserve the original meaning, uncertainty, numbers, and literal technical content. Use the language requested by the user or appropriate to the current task." |
| `full-skill` | Load and apply `SKILL.md`, with its linked reference examples available |

All conditions still have the host model's ordinary system and developer instructions. The baseline is not an unprompted or instruction-free model.

The initial pilot used three independent Codex subagents, each with one batch of the same 24 cases. Each subagent had no parent conversation history, was instructed to treat cases independently, and could read only its assigned input and, for the skill condition, the skill and reference. It did not receive scoring criteria or prior conclusions. The cases were **not** separate fresh model sessions within each batch.

## Inputs and scoring

- [cases.json](cases.json): 24 conversations, including Chinese, English, and mixed-language tasks.
- [rubric.json](rubric.json): semantic and format invariants, fixed before generating responses.
- [holdout-cases.json](holdout-cases.json) and [holdout-rubric.json](holdout-rubric.json): eight new transfer cases, fixed before the revised skill's re-test. These were written by the same developer after seeing the initial failure; they are not an independently sampled benchmark.
- [retest-cases.json](retest-cases.json): the eight transfer cases plus two original regression cases.

A case passes semantic review only when every listed invariant passes. `needs_review` remains unresolved until a documented adjudication; it is not counted as a pass. A separate 1–5 clarity rating is a model opinion, not a measured comprehension outcome.

Initial responses were shuffled using seed `20261108` and reviewed by a separate subagent without condition labels. The reviewer received only the source conversations, frozen invariants, and shuffled responses. The developer then inspected the actual outputs and adjudicated flagged findings. This hides condition labels, but cannot prevent inference from wording and does not remove shared model biases. Both review layers used AI agents; no human comprehension test was conducted.

For literal and format checks:

```bash
python3 tools/check_responses.py evals/results/full-skill.json
python3 tools/check_responses.py evals/results/revised-skill.json --cases evals/retest-cases.json
```

The checker verifies case coverage, several exact literals, one JSON contract, and one no-change request. It deliberately **does not** classify all languages, infer semantic equivalence, or grade prose. A response that changes the meaning can pass this checker; a unit test demonstrates that limitation.

## Run another comparison

1. Freeze realistic cases and their invariants before generation. Keep rubric files away from the subjects.
2. Use the same model, host instructions, settings, and task inputs for every condition. Prefer fresh contexts per case and multiple samples for stronger evidence.
3. Prepare prompts with `python3 tools/make_prompt.py baseline`, `short-prompt`, or `full-skill`. The helper emits a portable batch prompt; it does not call a model. The pilot used file-based subagent instructions instead of this helper, so transport differs.
4. Save each output as `{"responses":[{"id":"c01","response":"actual answer"}, ...]}`. Preserve failures without editing model responses.
5. Run exact checks, then give anonymized responses and the fixed rubric to a separate reviewer. Record disagreements and score meaning separately from clarity.
6. Report all conditions, model/settings where known, prompt versions, failures, and sample count. For claims about comprehension, add a human task with correctness and time-to-understanding measurements.

The helper uses the current skill. To reproduce the initial input wording, substitute [snapshots/initial-skill.txt](snapshots/initial-skill.txt), a byte-for-byte snapshot whose reference paths are relative to the original repository root. Exact backend model revision and sampling settings were not exposed by the host in this pilot, so exact output reproduction is not promised.

See [pilot-report.md](pilot-report.md) for results and [results/](results/) for raw responses, reviews, and manifests.
