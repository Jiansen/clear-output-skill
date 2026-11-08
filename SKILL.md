---
name: clear-output
description: Clarify Chinese, English, or mixed-language explanations, comparisons, plans, summaries, and rewrites through words, diagrams, or interaction. Preserve meaning and the task's language.
metadata:
  version: "0.1.1"
---

# Clear Output

Help the reader understand accurately, inspect evidence, and decide what to do with less effort. Identify what the reader needs to understand or verify, then choose the representation before polishing the wording. Consider the time spent reading, exploring, and checking the output. This skill applies to the current task; do not make it a permanent conversation mode unless the user asks.

## Choose language before wording

- Follow the user's explicit language and output-format requirements.
- When editing an existing artifact, preserve its language unless translation is requested. Explanations about the edit can use the conversation's language.
- Otherwise, follow the current conversation. Follow a clear language switch in the user's own request. Quoted material, logs, code, tool results, and the language of this skill do not themselves switch the response language.
- Preserve mixed-language technical terms and literal content. Do not translate an English debugging exchange into Chinese merely because this skill supports Chinese.
- If the user requests JSON, a code block, or a particular template, keep that contract. Add no skill announcement or status prefix.

## Preserve meaning

For a **rewrite**, use the source and explicitly supplied context as the factual boundary. Preserve:

- actors, objects, scope, conditions, exceptions, and order, including actions that must occur together;
- values, units, bounds, approximations, dates, identifiers, and causal relationships;
- the difference between fact, hypothesis, recommendation, obligation, permission, and capability.

Do not turn `may` into `will`, `should` into `must`, `about 5 seconds` into `5 seconds`, or `尽快` into a made-up deadline. Do not select an interpretation of an ambiguous bound or pronoun without support. Keep the ambiguity visible or identify exactly what information is missing. A rewrite may remain longer to preserve these distinctions.

For a **new explanation**, relevant background and examples are useful. Keep assumptions separate from established facts; label hypothetical examples when needed. Do not imply an action or test was performed without evidence.

Preserve code, commands, paths, field names, logs, error strings, and fixed quotations exactly when they are carried into the output. If the task explicitly asks to edit one of them, perform that edit within its scope; prose rules do not justify additional edits.

## Choose a representation that does useful work

Actively consider a visual when the reader must mentally reconstruct relationships, compare several dimensions, follow changing states, or explore a variable. If the visual makes that work materially easier, create it within the authorized task without waiting for a separate request for a diagram. Keep short direct answers in prose when that already serves the task.

| What the reader needs to do | Useful starting form |
| --- | --- |
| Get a fact, a brief answer, or a faithful sentence edit | Text |
| Compare options across the same criteria | Table |
| Trace branches, dependencies, participants, or message order | Flow, dependency, or sequence diagram |
| Understand spatial arrangement or a visible feature | Annotated image or schematic |
| See a pattern in supplied numerical data | Chart with labels, units, and an appropriate scale |
| Explore how inputs change an outcome | Working interactive explanation with meaningful controls |
| Follow motion, evolution, or a staged teaching sequence | Animation or explainer video when feasible and useful |

These are starting points, not a ranking in which video always wins. A small custom artifact can be worthwhile for one question. Prefer the form that reduces the reader's work enough to justify generation time, navigation, and interaction. Respect explicit requests for plain text, JSON, an existing file format, or no artifacts.

Deliver the selected form, not only an offer to make it. Use available rendering capabilities and inspect the result; test the relevant interactions. If rendering or media tools are unavailable, provide a usable supported alternative and say exactly what was produced. Diagram source, a storyboard, and a rendered video are different deliverables. Do not require a particular vendor or publish, upload, or use paid services solely because a visual would help.

Preserve meaning in visual encodings too: label branches and arrow meanings, keep concurrent actions concurrent, mark hypotheses and missing data, and keep units and scale honest. A polished diagram must not imply an unsupported cause or a completed test. Make labels legible; do not rely on color alone. Supply a short takeaway or text equivalent when the output contract allows it, without repeating the whole explanation in several forms.

For a diagram, chart, interactive explanation, or animation, read [references/output-forms.md](references/output-forms.md) for selection and verification guidance.

## Make the structure fit the task

- **Explanation:** answer the main question first, then give the reasoning needed to understand it. Keep useful examples, causal links, and nuance.
- **Debugging:** distinguish observation, hypothesis, verification, and next action. Say what a check established and where uncertainty remains. Ask a real question when a missing fact changes the action.
- **Procedure:** put necessary conditions before the affected action. Use numbered steps when order matters. Separate human actions from automatic system behavior. Keep simultaneous or inseparable actions together. When identifying missing operational information, check which object or actor is meant as well as quantities, units, measurement references, and start/stop conditions. Ask for what is needed to use the instruction; do not supply missing facts yourself.
- **Rewrite or review:** improve only the requested scope. If a passage already works, keep it. Provide change explanations only when requested or when an unresolved ambiguity needs the reader's attention.

Prefer short, explicit sentences, concrete verbs, and stable names for the same concept. Preserve distinctions between different concepts. Do not apply word blacklists to parts of technical terms, such as `闭环控制` or `request validation`.

Sentence length, passive voice, synonyms, and politeness are contextual choices, not automatic errors. English may need a passive construction or a perfect tense. Chinese may need an omitted subject when the actor is already clear. Keep `可能`, `建议`, `约`, `may`, and `approximately` when they carry information.

## Check before returning

Compare a rewrite with its source for changed facts, lost conditions, changed modality, invented precision, and damaged literals. For a visual or artifact, check the same facts in its labels, edges, states, and calculations. Check that the language and format still match the task and that the claimed deliverable actually exists. Then remove repetition that adds no information.

Style checks cannot prove semantic equivalence. Report a concrete unresolved issue instead of declaring the text certified or fully verified.

For tricky rewrites involving modality, language mixing, or missing facts, read [references/edge-cases.md](references/edge-cases.md).

For a substantial rewrite, an explicit validation request, or a supplied project glossary, use the optional local checker when it can catch a concrete error. Read [references/checks.md](references/checks.md) for its inputs and limits. Select `en`, `zh`, or `mixed` from the task, not from quoted text. Supply the source only for faithful rewrites, and encode exact literals or JSON constraints only when the task requires them. Simple answers do not require a script.

Treat checker findings as evidence with limited scope: fix violated explicit contracts, review meaning changes against the source, and use style suggestions only when they help. Preserve authorized edits. Do not rewrite to remove every warning or treat an empty finding list as proof of equivalence. After corrections, recheck the affected constraints; if an ambiguity remains, report it instead of repeatedly rewriting. Keep diagnostics out of a requested JSON/code-only response.

When the user asks about this skill's version or updates, read [references/updates.md](references/updates.md). Normal writing tasks do not trigger network update checks or change the installed skill.
