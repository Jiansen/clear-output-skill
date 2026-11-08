# Contributing to Clear Output

Start with a task someone actually needed to understand. A small, reproducible example is more useful than another universal writing rule.

- [Share a clarity example](https://github.com/Jiansen/clear-output-skill/issues/new?template=clarity-feedback.yml): include the input, actual output, agent/model, skill version, and the specific improvement or failure. Chinese and English are welcome.
- Suggest an example from everyday life, study, teamwork, or technical work. Use fictional data or material you have permission to publish.
- For a change to the skill, explain what meaning must remain intact and which case demonstrates the need. Follow the artifact's existing language.

For Python changes, run `python3 -m unittest discover -s tests -v`. For changes to the README example source, run `node evals/browser/render-readme-examples.mjs` and inspect the generated cards; setup instructions are in [assets/readme/README.md](assets/readme/README.md). For the public demo, see [site/README.md](site/README.md).

Do not present authored examples as raw model A/B results. Keep community feedback distinct from measured evaluation, and include the limits of any claimed result. Maintainers handle release versions and publishing.
