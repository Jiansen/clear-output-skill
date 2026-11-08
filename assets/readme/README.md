# Compact README examples

Six visible before/after examples, in English and Chinese. The first three are authored fictional scenarios: choosing between travel plans, organizing workshop notes, and interpreting a class survey. The last three preserve the original [showcase](../showcase/README.md) examples: release conditions, debugging evidence, and retry timing.

These are editorial demonstrations of presentation, not raw model outputs, measured A/B results, actual travel prices, meeting records, or research data. Keep that context when reusing a card.

[Open the editable HTML](examples.html) from a local checkout or download it to use the language selector and retry sliders. It works offline without external fonts, packages, or services. GitHub's file view does not execute HTML. Each README card links to its full-resolution image; the corresponding input is also readable as text in the HTML.

| Example | English | 中文 | What becomes easier to inspect |
| --- | --- | --- | --- |
| Choices | [PNG](choices-en.png) | [PNG](choices-zh.png) | Cost, time, changes, and the priority that determines the choice |
| Meeting notes | [PNG](meeting-en.png) | [PNG](meeting-zh.png) | The decision, action owners, deadlines/dependencies, and undecided budget |
| Survey reading | [PNG](reading-en.png) | [PNG](reading-zh.png) | 18 of 30 responses (60%) and the limit on interpreting preference as learning benefit |
| Release process | [PNG](release-en.png) | [PNG](release-zh.png) | Parallel checks, both-pass deployment, and either-failure stopping the release |
| Debugging | [PNG](debugging-en.png) | [PNG](debugging-zh.png) | The exact error, an unconfirmed hypothesis, and the next check |
| Retry exploration | [PNG](retry-en.png) · [GIF](retry-en.gif) | [PNG](retry-zh.png) · [GIF](retry-zh.gif) | How base delay and retry count change waiting and attempt count |

The retry GIF uses real screenshots after operating the HTML controls: `(base delay, retries)` goes through `(1,3)`, `(2,3)`, `(2,4)`, `(2,0)`, and `(1,3)`. Waiting totals are 7, 14, 30, 0, and 7 seconds; execution is excluded. A 10-second GIF loop is presentation timing, not a simulation of those delays. The PNG is static; the HTML controls work.

## Rebuild

```bash
npm ci --prefix evals/browser --ignore-scripts
node evals/browser/render-readme-examples.mjs
```

Requires Chrome (or a Chromium path in `CLEAR_OUTPUT_BROWSER`) and FFmpeg. It generates 12 PNGs at twice the card's CSS resolution and two GIFs. It verifies the original technical examples' wording and labels, the fictional data, layout bounds, all 72 retry input combinations, keyboard operation, language switching, a narrow-screen HTML layout, and absence of runtime HTTP requests. Results are in [render-checks.json](render-checks.json). Browser checks are optional and are separate from the ordinary Python CI suite.

The compact cards omit repeated poster branding and repository footers. The [original social assets](../showcase/README.md) remain available unchanged. The skill release ZIP excludes these README/media assets; they are in the repository and its source archive.
