# Sources and design choices

Clear Output's instructions, examples, fixtures, and Python helpers were written for this project. The following works informed the design; their text, code, and dictionaries are not redistributed here.

| Source | Revision reviewed | Useful influence |
| --- | --- | --- |
| [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) | `f38838aee0504fae07ef057667182a7c5af4ffe6` | Applying controlled-language ideas to agent output |
| [dualface/ste-zh](https://github.com/dualface/ste-zh) | `22f868ec3ab77e902571379ad1eaccee4c38fdac` | Separating completed work from verified outcomes |
| [mzopedia/simplified-technical-chinese](https://github.com/mzopedia/simplified-technical-chinese) | `90ad0f004b26d7a66e286980b5efaf4769ad8584` | Testable writing checks and explicit scope |
| [Fenng/Tech-Doc-Style-Chinese](https://github.com/Fenng/Tech-Doc-Style-Chinese) | `b119d01c9bb7cd132b3c62fafdff34227c4410d1` | Prioritizing source fidelity in Chinese documentation |
| [JICio/simplified-technical-chinese](https://github.com/JICio/simplified-technical-chinese) | `6ed8a7ce8d5ee1d6230ffba335932984a5a1f153` | Choosing a useful output form and supporting language-specific guidance |

[Andrej Karpathy's post](https://x.com/karpathy/status/2105819303471976479) discusses making AI output easier to understand, including simplified technical language and useful visual forms. The design here treats that as a motivation, not experimental proof. The review also used a [public transcript](https://superx.so/creators/karpathy) because the accessible original embed was truncated.

[ASD-STE100](https://www.asd-ste100.org/) is an English controlled-language specification. This project does not claim to implement the full standard, certify compliance, provide an official Chinese edition, or have ASD endorsement.

## Deliberate choices

1. Language routing and writing style are separate. Supporting Chinese does not require translating English tasks.
2. Source fidelity takes precedence over brevity. Approximation, uncertainty, modality, and unresolved ambiguity are information.
3. Technical literals and terms need contextual protection. A substring blacklist cannot distinguish a slogan from a control-system term.
4. Sentence length and readable formatting are guidance, not proof of comprehension.
5. The evaluation checks observable behavior and records raw outputs. It does not use a style score as a substitute for meaning.

No third-party license is replaced by this project's MIT license. If future contributions copy or adapt source material, include the source's required attribution and license terms.
